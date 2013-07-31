from wikimetrics.utils import stringify
from report import ReportNode
from multi_project_metric_report import MultiProjectMetricReport


__all__ = ['AggregateReport']


class Aggregation(object):
    SUM = 'Sum'
    AVG = 'Average'
    STD = 'Standard Deviation'


class AggregateReport(ReportNode):
    """
    Represents the output-shaping node that looks at a
    single metric's results over a cohort and returns any combination of:
    
        * individual results
        * a sum of the individual results
        * an average over the individual results
        * the standard deviation over the individual results
    
    Whether or not to return these is controlled by parameters passed to the constructor.
    """
    
    show_in_ui = True
    
    def __init__(
        self,
        cohort,
        metric,
        individual=False,
        aggregate=True,
        aggregate_sum=True,
        aggregate_average=False,
        aggregate_std_deviation=False,
        *args,
        **kwargs
    ):
        super(AggregateReport, self).__init__(
            parameters=stringify(metric.data),
            *args,
            **kwargs
        )
        
        self.individual = individual
        self.aggregate = aggregate
        self.aggregate_sum = aggregate_sum
        self.aggregate_average = aggregate_average
        self.aggregate_std_deviation = aggregate_std_deviation
        
        self.children = [MultiProjectMetricReport(
            cohort,
            metric,
            name=self.name,
        )]
    
    def finish(self, multi_project_results):
        aggregated_results = dict()
        
        # TODO: what in the world is going on with async / non-async results
        #multi_project_results = multi_project_results[0].result
        
        if self.aggregate:
            if self.aggregate_sum:
                aggregated_results[Aggregation.SUM] = self.calculate(
                    multi_project_results,
                    Aggregation.SUM
                )
            if self.aggregate_sum:
                aggregated_results[Aggregation.AVG] = self.calculate(
                    multi_project_results,
                    Aggregation.AVG
                )
            if self.aggregate_sum:
                aggregated_results[Aggregation.STD] = self.calculate(
                    multi_project_results,
                    Aggregation.STD
                )
        
        if self.individual:
            aggregated_results['individual results'] = multi_project_results
        
        return aggregated_results
    
    def calculate(self, list_of_results, type_of_aggregate):
        # TODO: terrible redo this
        aggregation = dict()
        helper = dict()
        for results_by_user in list_of_results:
            for user_id in results_by_user.keys():
                for key in results_by_user[user_id]:
                    if not key in aggregation:
                        aggregation[key] = 0
                        helper[key] = dict()
                        helper[key]['sum'] = 0.0
                        helper[key]['count'] = 0
                    
                    value = results_by_user[user_id][key]
                    if not value:
                        value = 0
                    
                    helper[key]['sum'] += value
                    helper[key]['count'] += 1
                    
                    if type_of_aggregate == Aggregation.SUM:
                        aggregation[key] = helper[key]['sum']
                    elif type_of_aggregate == Aggregation.AVG:
                        if helper[key]['count'] != 0:
                            aggregation[key] = helper[key]['sum'] / helper[key]['count']
                        else:
                            aggregation[key] = 0
                    elif type_of_aggregate == Aggregation.STD:
                        aggregation[key] = 'Not Implemented'
                        pass
        
        return aggregation
    
    def __repr__(self):
        return '<AggregateReport("{0}")>'.format(self.persistent_id)