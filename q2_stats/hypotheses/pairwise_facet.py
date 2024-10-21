
def mann_whitney_u_facet(ctx, distribution, facet='within'):
    mann_whitney_u = ctx.get_action('stats', 'mann_whitney_u')
    facet_within = ctx.get_action('stats', 'facet_within')
    facet_across = ctx.get_action('stats', 'facet_across')
    collate_stats = ctx.get_action('stats', 'collate_stats')

    if facet == 'within':
        dists, = facet_within(distribution)
    elif facet == 'across':
        dists, = facet_across(distribution)
    else:
        raise ValueError('`facet` should be "within" or "across"')

    stats = {}
    for key, dist in dists.items():
        stats[key], = mann_whitney_u(dist, 'all-pairwise')

    stats, = collate_stats(stats)
    return stats


def wilcoxon_srt_facet(ctx, distribution, ignore_empty_comparator = True):
    wilcoxon_srt = ctx.get_action('stats', 'wilcoxon_srt')
    facet_across = ctx.get_action('stats', 'facet_across')
    collate_stats = ctx.get_action('stats', 'collate_stats')

    dists, = facet_across(distribution)

    stats = {}
    for key, dist in dists.items():
        stats[key], = wilcoxon_srt(
            dist, 'consecutive',
            ignore_empty_comparator=ignore_empty_comparator)

    stats, = collate_stats(stats)
    return stats
