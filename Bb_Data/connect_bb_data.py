import snowflake.connector
import json
import pandas as pd


def get_cred():
    with open('cred.json', 'r') as f:
        cred = json.load(f)
        return cred


def data_connection():
    cred = get_cred()
    connection = snowflake.connector.connect(
        user=cred['username'],
        password=cred['password'],
        account=cred['account_name'],
        warehouse=cred['warehouse'],
        database=cred['database']

    )

    with connection as conn:
        query = """ select * from BBD_REPORTING.PLATFORM_LMS_SESSION_BY_DAY_OF_WEEK_AND_HOUR_OF_DAY where date > '2021-02-01' order by date,TWO_HOURS_INTERVAL_TWELVE_HOURS_FORMAT,indexed_day;
                """
        cs = conn.cursor()
        cs.execute(query)
        rows = cs.fetchall()
        # for row in rows:
        #     return row

        columns = list(map(lambda x: x[0], cs.description))

        df = pd.DataFrame(rows, columns=columns)

        df.to_csv('LMS_Session.csv', index=False)

        print(df)


if __name__ == '__main__':
    data_connection()
