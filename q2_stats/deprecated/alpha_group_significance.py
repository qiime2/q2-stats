import pandas as pd

import qiime2


def alpha_group_significance(ctx, alpha_diversity, metadata, columns,
                             subject='', timepoint=''):
    alpha_to_dist = ctx.get_action('stats', 'prep_alpha_distribution')
    wilcoxon_srt_facet = ctx.get_action('stats', 'wilcoxon_srt_facet')
    mann_whitney_u_facet = ctx.get_action('stats', 'mann_whitney_u_facet')
    plot_rainclouds = ctx.get_action('stats', 'plot_rainclouds')

    dist, = alpha_to_dist(alpha_diversity, metadata, columns,
                          subject, timepoint)
    if subject != '':
        if timepoint != '':
            stats, = wilcoxon_srt_facet(dist, ignore_empty_comparator=True)
        else:
            raise ValueError('Missing timepoints for subjects')
    else:
        if timepoint != '':
            stats, = mann_whitney_u_facet(dist, facet='across')
        else:
            stats, = mann_whitney_u_facet(dist, facet='within')

    viz, =  plot_rainclouds(dist, stats)

    return dist, stats, viz


def prep_alpha_distribution(alpha_diversity: pd.Series,
                            metadata: qiime2.Metadata,
                            columns: list[str], subject: str = '',
                            timepoint: str = '',
                            ) -> pd.DataFrame:
    metadata = metadata.filter_ids(alpha_diversity.index)
    md_df = metadata.to_dataframe()

    df = md_df[columns]
    dist = df.melt(ignore_index=False, var_name='class', value_name='level')

    dist['measure'] = alpha_diversity
    if subject != '':
        dist['subject'] = md_df[subject]
    if timepoint != '':
        dist['group'] = md_df[timepoint]

    dist = dist.reset_index(names='id')

    dist['measure'].attrs.update({
        'title': alpha_diversity.name or 'alpha-diversity'
    })

    if subject != '':
        dist['subject'].attrs.update({
            'title': subject
        })
    if timepoint != '':
        dist['group'].attrs.update({
            'title': timepoint
        })


    return dist
