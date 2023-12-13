import git
from django import template


register = template.Library()


@register.filter
def index(indexable, i):
    return indexable[i]


@register.filter
def replace(self, valor):
    return self.replace(str(valor).split(',')[0], valor.split(',')[1])


@register.filter
def get_object(objects, id):
    for object in objects:
        if object.id == id:
            return object


@register.inclusion_tag('tags/button.html')
def button(text, tipo, *args, **kwargs):
    return {'text': text, 'tipo': tipo}


@register.inclusion_tag('tags/user_modified.html')
def user_modified_button(user, date_modified):
    context = {
        'user': user.first_name + ' ' + user.last_name ,
        'modified': date_modified
    }
    return context


@register.inclusion_tag('tags/git_version.html')
def get_git_version():
    return {
        'git_version': git.Repo(search_parent_directories=True)\
                            .head.object.hexsha[:7]
        }
