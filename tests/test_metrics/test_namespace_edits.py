from datetime import datetime
from nose.tools import assert_true, assert_equal
from tests.fixtures import QueueDatabaseTest, DatabaseTest, mediawiki_project

from wikimetrics.configurables import db
from wikimetrics.metrics import NamespaceEdits
from wikimetrics.enums import TimeseriesChoices
from wikimetrics.models import MetricReport


class NamespaceEditsDatabaseTest(DatabaseTest):
    def setUp(self):
        DatabaseTest.setUp(self)
        self.common_cohort_1()
    
    def test_filters_out_other_editors(self):
        self.common_cohort_1(cohort=False)
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2012-12-31 22:59:59',
            end_date='2013-01-01 12:00:00',
        )
        results = metric(self.editor_ids, self.mwSession)

        assert_equal(len(results), 4)

    def test_runs_for_an_entire_wiki(self):
        self.common_cohort_1(cohort=False)
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2012-12-31 22:59:59',
            end_date='2013-01-01 12:00:00',
        )
        results = metric(None, self.mwSession)

        assert_equal(len(results), 8)
        assert_equal(results[self.editors[0].user_id]['edits'], 3)
        assert_equal(results[self.editors[1].user_id]['edits'], 1)
        # NOTE: this is a bit precarious as it assumes the order of test data inserts
        assert_equal(results[self.editors[0].user_id + 4]['edits'], 3)

    def test_finds_edits(self):
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2012-12-31 22:59:59',
            end_date='2013-01-01 12:00:00',
        )
        results = metric(self.editor_ids, self.mwSession)
        
        assert_true(results is not None)
        assert_equal(results[self.editors[0].user_id]['edits'], 3)
        assert_equal(results[self.editors[1].user_id]['edits'], 1)
    
    def test_reports_zero_edits(self):
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2011-01-01 00:00:00',
            end_date='2011-02-01 00:00:00',
        )
        results = metric(self.editor_ids, self.mwSession)
        
        assert_true(results is not None)
        assert_equal(results[self.editors[0].user_id]['edits'], 0)

    def test_validates_properly(self):
        
        metric = NamespaceEdits()
        # defaults allow this to validate
        assert_true(metric.validate())
        
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2013-06-30 00:00:00',
            end_date='2013-07-01 00:00:00',
        )
        # values above are valid
        assert_true(metric.validate())
        
        metric = NamespaceEdits(
            start_date='blah',
        )
        assert_true(not metric.validate())

    def test_filters_out_other_editors_with_archive(self):
        self.archive_revisions()
        self.test_filters_out_other_editors()

    def test_runs_for_an_entire_wiki_with_archive(self):
        self.archive_revisions()
        self.test_runs_for_an_entire_wiki()

    def test_finds_edits_with_archive(self):
        self.archive_revisions()
        self.test_finds_edits()

    def test_reports_zero_edits_with_archive(self):
        self.archive_revisions()
        self.test_reports_zero_edits()

    def test_validates_properly_with_archive(self):
        self.archive_revisions()
        self.test_validates_properly()


class NamespaceEditsFullTest(QueueDatabaseTest):
    def setUp(self):
        QueueDatabaseTest.setUp(self)
        self.common_cohort_1()
    
    def test_namespace_edits(self):
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2012-12-31 22:59:59',
            end_date='2013-01-01 12:00:00',
        )
        report = MetricReport(
            metric, self.cohort.id,
            self.editor_ids, mediawiki_project
        )
        results = report.task.delay(report).get()

        # for some reason, during testing with archive, these users lose the session
        # when they're being operated on in the queue
        self.mwSession.add_all(self.editors)
        
        assert_true(results is not None)
        assert_equal(results[self.editor(0)]['edits'], 3)
    
    def test_namespace_edits_namespace_filter(self):
        metric = NamespaceEdits(
            namespaces=[3],
            start_date='2012-12-31 22:59:59',
            end_date='2014-02-01 00:00:00',
        )
        report = MetricReport(
            metric, self.cohort.id,
            self.editor_ids, mediawiki_project
        )
        results = report.task.delay(report).get()

        # for some reason, during testing with archive, these users lose the session
        # when they're being operated on in the queue
        self.mwSession.add_all(self.editors)
        
        assert_true(results is not None)
        assert_equal(results[self.editor(0)]['edits'], 0)
    
    def test_namespace_edits_namespace_filter_all_namespaces(self):
        metric = NamespaceEdits(
            namespaces=[],
            start_date='2012-12-31 22:59:59',
            end_date='2013-01-01 12:00:00',
        )
        report = MetricReport(
            metric, self.cohort.id,
            self.editor_ids, mediawiki_project
        )
        results = report.task.delay(report).get()

        # for some reason, during testing with archive, these users lose the session
        # when they're being operated on in the queue
        self.mwSession.add_all(self.editors)
        
        assert_true(results is not None)
        assert_equal(results[self.editor(0)]['edits'], 3)
    
    def test_namespace_edits_with_multiple_namespaces(self):
        metric = NamespaceEdits(
            namespaces=[0, 209],
            start_date='2012-12-31 22:59:59',
            end_date='2013-01-01 12:00:00',
        )
        report = MetricReport(
            metric, self.cohort.id,
            self.editor_ids, mediawiki_project
        )
        results = report.task.delay(report).get()

        # for some reason, during testing with archive, these users lose the session
        # when they're being operated on in the queue
        self.mwSession.add_all(self.editors)
        
        assert_true(results is not None)
        assert_equal(results[self.editor(0)]['edits'], 3)
    
    def test_namespace_edits_with_multiple_namespaces_when_passing_csv_string(self):
        metric = NamespaceEdits(
            namespaces='0, 209',
            start_date='2012-12-31 22:59:59',
            end_date='2013-01-01 12:00:00',
        )
        report = MetricReport(
            metric, self.cohort.id,
            self.editor_ids, mediawiki_project
        )
        results = report.task.delay(report).get()

        # for some reason, during testing with archive, these users lose the session
        # when they're being operated on in the queue
        self.mwSession.add_all(self.editors)
        
        assert_true(results is not None)
        assert_equal(results[self.editor(0)]['edits'], 3)

    def test_namespace_edits_with_archive(self):
        self.archive_revisions()
        self.test_namespace_edits()

    def test_namespace_edits_namespace_filter_with_archive(self):
        self.archive_revisions()
        self.test_namespace_edits_namespace_filter()

    def test_namespace_edits_namespace_filter_all_namespaces_with_archive(self):
        self.archive_revisions()
        self.test_namespace_edits_namespace_filter_all_namespaces()

    def test_namespace_edits_with_multiple_namespaces_with_archive(self):
        self.archive_revisions()
        self.test_namespace_edits_with_multiple_namespaces()

    def test_namespace_edits_multi_namespaces_when_passing_csv_string_with_archive(self):
        self.archive_revisions()
        self.test_namespace_edits_with_multiple_namespaces_when_passing_csv_string()


class NamespaceEditsTimestampTest(DatabaseTest):
    
    def setUp(self):
        DatabaseTest.setUp(self)
        self.create_test_cohort(
            editor_count=1,
            revisions_per_editor=5,
            revision_timestamps=[[
                20130101000000,
                20130101010000,
                20130101010100,
                20130101020100,
                20130101020101,
            ]],
            revision_lengths=10
        )
    
    def test_timestamp_range_hour(self):
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2013-01-01 00:00:00',
            end_date='2013-01-01 01:00:00',
        )
        results = metric(self.editor_ids, self.mwSession)
        assert_equal(results[self.editors[0].user_id]['edits'], 1)
        
    def test_timestamp_range_minutes(self):
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2013-01-01 00:00:00',
            end_date='2013-01-01 01:01:00',
        )
        results = metric(self.editor_ids, self.mwSession)
        assert_equal(results[self.editors[0].user_id]['edits'], 2)
        
    def test_timestamp_range_seconds(self):
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2013-01-01 02:01:00',
            end_date='2013-01-01 02:01:01',
        )
        results = metric(self.editor_ids, self.mwSession)
        assert_equal(results[self.editors[0].user_id]['edits'], 1)

    def test_timestamp_range_hour_with_archive(self):
        self.archive_revisions()
        self.test_timestamp_range_hour()

    def test_timestamp_range_minutes_with_archive(self):
        self.archive_revisions()
        self.test_timestamp_range_minutes()

    def test_timestamp_range_seconds_with_archive(self):
        self.archive_revisions()
        self.test_timestamp_range_seconds()


class NamespaceEditsTimeseriesTest(DatabaseTest):
    
    def setUp(self):
        DatabaseTest.setUp(self)
        self.common_cohort_1()
    
    def test_the_setup_worked(self):
        assert_equal(len(self.editors), 4)
        assert_equal(len(self.revisions), 16)
        assert_equal(self.revisions[-1].rev_timestamp, datetime(2014, 01, 02))
        assert_equal(self.revisions[0].rev_timestamp, datetime(2012, 12, 31, 23))
    
    def test_no_timeseries(self):
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2012-12-31 00:00:00',
            end_date='2013-01-02 00:00:00',
            timeseries=TimeseriesChoices.NONE,
        )
        results = metric(self.editor_ids, self.mwSession)
        
        assert_equal(results[self.editors[0].user_id]['edits'], 3)
    
    def test_timeseries_day(self):
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2012-12-31 10:00:00',
            end_date='2013-01-02 00:00:00',
            timeseries=TimeseriesChoices.DAY,
        )
        results = metric(self.editor_ids, self.mwSession)
        
        assert_equal(
            results[self.editors[0].user_id]['edits'],
            {
                '2012-12-31 10:00:00' : 1,
                '2013-01-01 00:00:00' : 2,
            }
        )
    
    def test_timeseries_hour(self):
        metric = NamespaceEdits(
            namespaces=[0],
            start_date='2013-01-01 00:00:00',
            end_date='2013-01-01 02:00:00',
            timeseries=TimeseriesChoices.HOUR,
        )
        results = metric(self.editor_ids, self.mwSession)
        
        assert_equal(
            results[self.editors[0].user_id]['edits'],
            {
                '2013-01-01 00:00:00' : 1,
                '2013-01-01 01:00:00' : 1,
            }
        )

    def test_no_timeseries_with_archive(self):
        self.archive_revisions()
        self.test_no_timeseries()

    def test_timeseries_day_with_archive(self):
        self.archive_revisions()
        self.test_timeseries_day()

    def test_timeseries_hour_with_archive(self):
        self.archive_revisions()
        self.test_timeseries_hour()
