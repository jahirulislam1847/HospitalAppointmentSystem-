from django.contrib import messages
from django.db.models import F, Q, Avg, Prefetch
from django.views.generic import ListView, DetailView
from django.shortcuts import redirect

from .models import DoctorProfile, DoctorSpecialized, DoctorReview
from .forms import DoctorReviewForm


class DoctorListView(ListView):
    model = DoctorProfile
    template_name = "doctorApp/doctor_list.html"
    context_object_name = "doctors"

    def get_queryset(self):
        queryset = (
            DoctorProfile.objects.select_related("user", "hospital")
            .prefetch_related("specialized", "qualification", "schedules")
            .all()
        )

        # Optional filters via query parameters
        search_query = self.request.GET.get("q")
        specialty_id = self.request.GET.get("specialty")

        if search_query:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search_query)
                | Q(hospital__name__icontains=search_query)
            )

        if specialty_id:
            queryset = queryset.filter(specialized__id=specialty_id)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["specialties"] = DoctorSpecialized.objects.all()
        context["selected_specialty"] = self.request.GET.get("specialty", "")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class DoctorDetailView(DetailView):
    model = DoctorProfile
    template_name = "doctorApp/doctor_detail.html"
    context_object_name = "doctor"
    pk_url_kwarg = "pk"  # Primary key corresponds to user_id

    def get_queryset(self):
        # Prefetch only active reviews (show=True) ordered by newest first
        active_reviews = Prefetch(
            "reviews",
            queryset=DoctorReview.objects.filter(show=True)
            .select_related("user")
            .order_by("-created_at"),
        )

        return DoctorProfile.objects.select_related("user").prefetch_related(
            "hospital", "specialized", "qualification", "schedules", active_reviews
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Atomically increment search count
        DoctorProfile.objects.filter(pk=obj.pk).update(
            search_count=F("search_count") + 1
        )
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.object

        # Calculate average rating & review count for active reviews
        active_reviews = doctor.reviews.all()
        context["reviews"] = active_reviews
        context["reviews_count"] = active_reviews.count()
        context["avg_rating"] = (
            active_reviews.aggregate(Avg("rating"))["rating__avg"] or 0
        )

        # Handle review form state for authenticated users
        context["user_review"] = None
        if self.request.user.is_authenticated:
            # Check if current logged-in user already left a review
            user_review = DoctorReview.objects.filter(
                doctor=doctor, user=self.request.user
            ).first()
            context["user_review"] = user_review
            context["review_form"] = DoctorReviewForm(instance=user_review)
        else:
            context["review_form"] = DoctorReviewForm()

        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You need to be logged in to leave a review.")
            return redirect("userApp:login")  # Replace with your login URL name

        self.object = self.get_object()
        doctor = self.object

        # Check if user already reviewed this doctor to update or create
        existing_review = DoctorReview.objects.filter(
            doctor=doctor, user=request.user
        ).first()

        form = DoctorReviewForm(request.POST, instance=existing_review)

        if form.is_valid():
            review = form.save(commit=False)
            review.doctor = doctor
            review.user = request.user
            review.save()

            action = "updated" if existing_review else "submitted"
            messages.success(request, f"Your review has been {action} successfully!")
            return redirect("doctorApp:doctor_detail", pk=doctor.pk)

        # If form is invalid, re-render context with errors
        context = self.get_context_data(object=doctor)
        context["review_form"] = form
        return self.render_to_response(context)


# class DoctorDetailView(DetailView):
#     model = DoctorProfile
#     template_name = 'doctorApp/doctor_detail.html'
#     context_object_name = 'doctor'
#     pk_url_kwarg = 'pk'  # Primary key corresponds to user_id

#     def get_queryset(self):
#         return DoctorProfile.objects.select_related(
#             'user'
#         ).prefetch_related(
#             'hospital',
#             'specialized',
#             'qualification',
#             'schedules'
#         )

#     def get_object(self, queryset=None):
#         obj = super().get_object(queryset)
#         # Atomically increment search view count
#         DoctorProfile.objects.filter(pk=obj.pk).update(search_count=F('search_count') + 1)
#         return obj
