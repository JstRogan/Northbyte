from django import forms

from articles.models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "image_url", "category", "excerpt", "content"]
        labels = {
            "title": "Title",
            "image_url": "Image URL",
            "category": "Category",
            "excerpt": "Short preview",
            "content": "Full article",
        }
        widgets = {
            "excerpt": forms.Textarea(attrs={"rows": 4}),
            "content": forms.Textarea(attrs={"rows": 12}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
