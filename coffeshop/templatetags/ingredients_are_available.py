from django import template

register = template.Library()

# Use the link below to know more about the custom template tags.
# https://docs.djangoproject.com/en/4.1/howto/custom-template-tags/

@register.filter
def ingredients_are_available(order):
    ingredients = order.order_ingredients.all()
    for ingredient in ingredients:
        if ingredient.quantity==0:
            return False
    return True