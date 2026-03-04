from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, FormView, UpdateView

from apps.properties.models import Property, PropertyImage
from apps.users.models import User
from .forms import PropertyForm, UserRegisterForm, ProfileUpdateForm


class HomeView(TemplateView):
    template_name = 'website/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_properties'] = (
            Property.objects.filter(is_active=True)
            .prefetch_related('images')
            .order_by('-created_at')[:6]
        )
        context['total_count'] = Property.objects.filter(is_active=True).count()
        return context


class PropertyListView(ListView):
    model = Property
    template_name = 'website/property_list.html'
    context_object_name = 'properties'
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Property.objects.filter(is_active=True)
            .prefetch_related('images')
            .order_by('-is_premium', '-created_at')
        )
        q = self.request.GET.get('q', '').strip()
        city = self.request.GET.get('city', '').strip()
        district = self.request.GET.get('district', '').strip()
        property_type = self.request.GET.get('type', '').strip()
        min_price = self.request.GET.get('min_price', '').strip()
        max_price = self.request.GET.get('max_price', '').strip()
        sort = self.request.GET.get('sort', '').strip()

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(address__icontains=q))
        if city:
            qs = qs.filter(city__icontains=city)
        if district:
            qs = qs.filter(district=district)
        if property_type:
            qs = qs.filter(property_type=property_type)
        if min_price.isdigit():
            qs = qs.filter(price__gte=min_price)
        if max_price.isdigit():
            qs = qs.filter(price__lte=max_price)
        if sort == 'price_asc':
            qs = qs.order_by('-is_premium', 'price', '-created_at')
        elif sort == 'price_desc':
            qs = qs.order_by('-is_premium', '-price', '-created_at')
        elif sort == 'newest':
            qs = qs.order_by('-is_premium', '-created_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        context['query_string'] = params.urlencode()
        return context


class PropertyDetailView(DetailView):
    model = Property
    template_name = 'website/property_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        return Property.objects.prefetch_related('images')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Property.objects.filter(pk=obj.pk).update(view_count=F('view_count') + 1)
        obj.refresh_from_db(fields=['view_count'])
        return obj


class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'website/property_form.html'

    def form_valid(self, form):
        requested_premium = bool(form.cleaned_data.get('is_premium', False))
        can_publish_premium = self.request.user.role in ['agent', 'admin']

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.is_premium = requested_premium and can_publish_premium
        self.object.save()

        uploaded_images = form.cleaned_data.get('images', [])
        for index, image in enumerate(uploaded_images):
            PropertyImage.objects.create(
                property=self.object,
                image=image,
                is_primary=(index == 0),
            )

        messages.success(self.request, "E'lon muvaffaqiyatli qo'shildi.")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.object.get_absolute_url()


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = UserRegisterForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Ro'yxatdan o'tdingiz.")
        return redirect('website:home')


class CabinetView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'website/cabinet.html'
    success_url = reverse_lazy('website:cabinet')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil ma'lumotlari yangilandi.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_properties = (
            Property.objects.filter(owner=self.request.user)
            .prefetch_related('images')
            .order_by('-created_at')
        )
        context['my_properties'] = my_properties[:8]
        context['my_properties_count'] = my_properties.count()
        context['my_active_count'] = my_properties.filter(is_active=True).count()
        context['my_premium_count'] = my_properties.filter(is_premium=True).count()
        return context
