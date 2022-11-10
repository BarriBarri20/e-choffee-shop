from django import forms
from .models import Order, Ingredient
from paypal.standard.forms import PayPalPaymentsForm

CHOICES = [('true', 'True'), ('false', 'False')]

class OrderUploadForm(forms.ModelForm):
    order_ingredients = forms.ModelMultipleChoiceField(queryset=Ingredient.objects.all(), label='Ingredient', required=True, widget=forms.SelectMultiple(attrs={'id': 'mySelect'}))
    class Meta:
        model = Order
        fields = ['is_activated', 'slug', 'name', 'order_price', 'description', 'order_image', 'order_ingredients']

class IngredientUploadForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['is_activated', 'is_optional', 'ingredient_slug', 'name', 'description', 'ingredient_price', 'quantity', 'ingredient_image']
from paypal.standard.forms import PayPalPaymentsForm


class CustomPayPalPaymentsForm(PayPalPaymentsForm):

    def get_html_submit_element(self):
        return """<button type="submit">Continue on PayPal website</button>"""