from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

Menu.add_item("home", MenuItem(_('mainmenu:home'),
                               reverse('main:home'),
                               exact_url=True
                               ))

Menu.add_item("main", MenuItem(_('mainmenu:login'),
                               reverse('main:login'),
                               exact_url=True,
                               check=lambda x: not x.user.is_authenticated
                               ))

Menu.add_item("main", MenuItem(_('mainmenu:experiments'),
                               reverse('experiments:home'),
                               exact_url=True,
                               check=lambda x: x.user.is_authenticated
                               ))

Menu.add_item("main", MenuItem(_('mainmenu:help'),
                               reverse('main:help'),
                               exact_url=False,
                               check=lambda x: x.user.is_authenticated
                               ))

Menu.add_item("main", MenuItem(_('mainmenu:administration'),
                               reverse('administration:home'),
                               exact_url=True,
                               check=lambda x: x.user.is_staff
                               ))

Menu.add_item("footer", MenuItem(_('footermenu:login'),
                                 reverse('main:login'),
                                 check=lambda x: not x.user.is_authenticated
                                 ))

Menu.add_item("footer", MenuItem(_('main:globals:logout'),
                                 reverse('main:logout'),
                                 check=lambda x: x.user.is_authenticated
                                 ))