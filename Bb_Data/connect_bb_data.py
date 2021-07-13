import snowflake.connector
import json
import pandas as pd
from snowflake.connector import ProgrammingError


class Blackboard_Data(object):

    def __init__(self):
        self.cred = self.get_cred()

        self.connection = self.data_connection()

    def get_cred(self):
        with open('/Users/edwardt/PycharmProjects/Bb_Dash/Bb_Data/cred.json', 'r') as f:
            cred = json.load(f)
            return cred

    def data_connection(self):
        # cred = get_cred()
        connection = snowflake.connector.connect(
            user=self.cred['username'],
            password=self.cred['password'],
            account=self.cred['account_name'],
            warehouse=self.cred['warehouse'],
            database=self.cred['database']

        )
        return connection

    def get_active_users(self, start, end):
        cur = self.connection.cursor()
        query = f" select * from BBD_REPORTING.PLATFORM_LMS_SESSION_BY_DAY_OF_WEEK_AND_HOUR_OF_DAY where date between '{start}' and '{end}' order by date,TWO_HOURS_INTERVAL_TWELVE_HOURS_FORMAT,indexed_day;"
        try:
            cur.execute(query)
            rows = cur.fetchall()
            # for row in rows:
            #     return row

            columns = list(map(lambda x: x[0], cur.description))

            df = pd.DataFrame(rows, columns=columns)

            df.to_csv('/Users/edwardt/PycharmProjects/Bb_Dash/Bb_Data/LMS_Session.csv', index=False)
        except ProgrammingError as err:
            print('Programming Error: {0}'.format(err))
        finally:
            cur.close()

    def get_tools_usage(self, start, end, semester):
        cur = self.connection.cursor()

        tool_usage = f"select date_trunc('month',to_date(ACTIVITY_TIME)) as month,count(DISTINCT course_id) as Courses,count(DISTINCT person_id) as Users,count(tool_id) as times_of_Acces,tool_name,tool_id from BBD_REPORTING.COURSE_TOOL_ACTIVITY_HOUR cta left join cdm_lms.course clc on cta.course_id = clc.id where ACTIVITY_TIME between '{start}'and '{end}' and clc.course_number like '%{semester}' group by month,tool_name,tool_id order by month, Courses, Users ASC"

        try:
            cur.execute(tool_usage)
            rows = cur.fetchall()
            # for row in rows:
            #     return row

            columns = list(map(lambda x: x[0], cur.description))

            df = pd.DataFrame(rows, columns=columns)

            df.to_csv('/Users/edwardt/PycharmProjects/Bb_Dash/Bb_Data/Tool_Usage.csv', index=False)

        except ProgrammingError as err:
            print('Programming Error: {0}'.format(err))
        finally:
            cur.close()


if __name__ == '__main__':
    bb = Blackboard_Data()
    bb.get_tools_usage('2021-02-1', '2021-04-01', 'S2021')

