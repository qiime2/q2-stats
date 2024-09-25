import pandas as pd

def set_pairwise_attrs(df: pd.DataFrame,
                        dist_a: pd.DataFrame, dist_b: pd.DataFrame,
                        group_measure: str,
                        test_stat: str, test_desc: str,
                        p_val: str, null_desc: str):

    df = df[['A:group', 'A:n', 'A:measure', 'B:group', 'B:n', 'B:measure',
             'n', 'test-statistic', 'p-value', 'q-value']]

    df['A:group'].attrs.update(dist_a['group'].attrs)
    df['B:group'].attrs.update(dist_b['group'].attrs)

    group_n = {
        'title': 'count',
        'description': 'The number of observations in the group.'
    }
    df['A:n'].attrs.update(group_n)
    df['B:n'].attrs.update(group_n)


    measure = lambda dist, group: {
        'title': f"{group_measure} of {dist['measure'].attrs['title']}",
        'description': f'The {group_measure} measure of {group}.'
    }
    df['A:measure'].attrs.update(measure(dist_a, 'group A'))
    df['B:measure'].attrs.update(measure(dist_b, 'group B'))

    df['n'].attrs.update({
        'title': 'count',
        'description': 'The number of observations used in the test.'
    })

    df['test-statistic'].attrs.update({
        'title': test_stat,
        'description': test_desc
    })

    df['p-value'].attrs.update({
        'title': p_val,
        'description': 'The probability of obtaining a test-statistic at least'
                       ' as extreme as observed under the null distribution.'
                       f' Where the null distribution is {null_desc}.'
    })

    return df