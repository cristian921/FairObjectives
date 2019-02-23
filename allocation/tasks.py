import celery
import pandas as pd
from celery import subtask
from dateutil.relativedelta import relativedelta
from django.http import HttpResponseRedirect
from datetime import datetime as dt
from allocation.models import Objective, UserResource, AggregatedPortfolio, PortfolioAsset, Series, ObjectiveSolution, \
    ObjectivePortfolioAsset
from allocation.optimization.optimization import optimize_ob
from allocation.utilities.utility import objectives_query_set_minus_savings_to_dict, difference_date, risk_corr, \
    return_assets

today = dt.strptime("2019-01-29", '%Y-%m-%d').date()


@celery.task(name="allo")
def objectives_allocation_task(request):
    objectives = Objective.objects.filter(user=request.user).order_by('time_horizon')
    resources = UserResource.objects.filter(user=request.user).order_by()
    yearly_savings = resources.first().monthly_savings * 12
    objectives = objectives_query_set_minus_savings_to_dict(objectives, yearly_savings)
    portfolio = AggregatedPortfolio.objects.filter(user=request.user).order_by()
    if portfolio:
        asset_portfolio = PortfolioAsset.objects.filter(aggregated_portfolio=portfolio).order_by()
        prices = Series.objects.filter(asset__portfolioasset__aggregated_portfolio=portfolio, date=today)

        prices_dict = dict()
        max_quotes = dict()
        for ap in asset_portfolio:
            max_quotes[ap.asset.codec] = ap.quote
            prices_dict[ap.asset.codec] = prices.filter(asset__codec=ap.asset.codec).first().price

        risks_dict = dict()
        returns_dict = dict()
        corr_dict = dict()
        initial_prices = dict()

        for obKey in objectives:
            start_date = difference_date(today, objectives[obKey]["time_horizon"])
            # print "start date", start_date
            # print "week", start_date.weekday()
            while start_date.weekday() > 4:
                #    print "qui"
                start_date += relativedelta(days=-1)

            # print "start date1", start_date
            in_prices = Series.objects.filter(asset__portfolioasset__aggregated_portfolio=portfolio,
                                              date=start_date).order_by('-date')

            prices_vett = dict()
            for ap in asset_portfolio:
                prices_vett[ap.asset.codec] = in_prices.filter(asset=ap.asset).first().price
            initial_prices[objectives[obKey]["time_horizon"]] = prices_vett

            asset_series = Series.objects.filter(asset__portfolioasset__aggregated_portfolio=portfolio,
                                                 date__range=(start_date, today))
            asset_series_dict = dict()
            for ap in asset_portfolio:
                asset_series_dict[ap.asset.codec] = pd.DataFrame(list(
                    asset_series.filter(asset=ap.asset).values()))

            risks, corr = risk_corr(asset_series_dict)
            an_returns, ab_returns = return_assets(asset_series_dict, start_date, today)
            risks_dict[objectives[obKey]["time_horizon"]] = risks
            returns_dict[objectives[obKey]["time_horizon"]] = an_returns
            corr_dict[objectives[obKey]["time_horizon"]] = corr
        solutions = optimize_ob(objectives, returns_dict, risks_dict, corr_dict,
                                initial_prices, max_quotes, prices_dict)
        # print json.dumps(solutions, indent=2)
        for obk in solutions:
            if "solution" in solutions[obk]:
                # print solutions[obk]["solution"]
                sol = ObjectiveSolution(feasible=solutions[obk]["solution"]["feasible"],
                                        savings_required=solutions[obk]["savings_required"], objective_id=obk,
                                        expected_return=solutions[obk]["solution"]["expected_return"],
                                        expected_risk=solutions[obk]["solution"]["expected_risk"])
                sol.save()
                if "quotes" in solutions[obk]["solution"]:
                    for ak in solutions[obk]["solution"]["quotes"]:
                        ob_port_asset = ObjectivePortfolioAsset(objective_solution=sol, asset_id=ak,
                                                                quote=solutions[obk]["solution"]["quotes"][ak],
                                                                date=today)
                        ob_port_asset.save()
    return "SUCCESS"

