from django import template

register = template.Library()


@register.filter(name='liked')
def liked(likes_map, post_id):
    if likes_map.get(post_id) is not None and likes_map.get(post_id):
        return 'true'
    else:
        return 'false'
