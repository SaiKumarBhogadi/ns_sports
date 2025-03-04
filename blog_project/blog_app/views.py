from django.shortcuts import render, redirect
from .forms import CustomUserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_app:login')  # Redirect to login page after registration
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'blog_app/register.html', {'form': form})



from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('blog_app:index')  # Redirect to home page after login
    else:
        form = AuthenticationForm()
    return render(request, 'blog_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('blog_app:login')  # Redirect to login page after logout


from django.db.models import Q
from django.shortcuts import render
from .models import Blog

def index(request):
    query = request.GET.get('q', '')  # Get search query from URL parameters
    blogs = Blog.objects.filter(status='approved').order_by('-created_at')  # Show all approved blogs

    if query:
        blogs = blogs.filter(
            Q(title__icontains=query) |  # Search by title (partial match)
            Q(author__username__icontains=query) |  # Search by username (partial match)
            Q(author__full_name__icontains=query)   # Search by full name (partial match)
        )

    return render(request, 'blog_app/index.html', {'blogs': blogs, 'query': query})




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile, Blog
from .forms import ProfileUpdateForm

@login_required
def profile_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)

    # Allow users to update their profile
    form = ProfileUpdateForm(instance=profile) if request.user == profile.user else None

    if request.user == profile.user and request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('blog_app:profile', username=username)

    return render(request, 'blog_app/profile.html', {'profile': profile, 'form': form})

@login_required
def blog_management_view(request):
    """Handles both admin and user blogs separately."""
    
    if request.user.is_superuser:
        pending_blogs = Blog.objects.filter(status='pending')
        approved_blogs = Blog.objects.filter(status='approved')
        rejected_blogs = Blog.objects.filter(status='rejected')
    else:
        pending_blogs = Blog.objects.filter(author=request.user, status='pending')
        approved_blogs = Blog.objects.filter(author=request.user, status='approved')
        rejected_blogs = Blog.objects.filter(author=request.user, status='rejected')

    return render(request, 'blog_app/blog_management.html', {
        'pending_blogs': pending_blogs,
        'approved_blogs': approved_blogs,
        'rejected_blogs': rejected_blogs,
    })







from django.shortcuts import render, get_object_or_404
from .models import Blog

def blog_list(request):
    blogs = Blog.objects.filter(status='approved').order_by('-created_at')
    return render(request, 'blog_app/blog_list.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, status='approved')
    return render(request, 'blog_app/blog_detail.html', {'blog': blog})




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Blog, BlogImage
from .forms import BlogForm

@login_required
def create_blog(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)  # Include request.FILES in form
        images = request.FILES.getlist('images')  # Get multiple images from form

        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.status = 'pending'  # Blog should be approved before being visible
            blog.save()

            # Save multiple images
            if images:  # Ensure images exist before saving
                for image in images:
                    BlogImage.objects.create(blog=blog, image=image)

            return redirect('blog_app:index')  # Redirect after submission
    else:
        form = BlogForm()

    return render(request, 'blog_app/create_blog.html', {'form': form})







from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def review_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    return render(request, 'blog_app/review_blog.html', {'blog': blog})


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Blog

@staff_member_required
def approve_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    blog.status = 'approved'
    blog.save()
    return HttpResponseRedirect(reverse('blog_app:profile', args=[blog.author.username]))

@staff_member_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    blog.delete()
    return HttpResponseRedirect(reverse('blog_app:profile', args=[blog.author.username]))

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Blog, RejectionReason

# Function to check if user is admin
def is_admin(user):
    return user.is_staff

from django.shortcuts import get_object_or_404, redirect
from .models import Blog, RejectionReason
from django.contrib import messages

@login_required
def reject_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == "POST":
        reason_text = request.POST.get("rejection_reason")

        # Ensure blog status is set to 'rejected'
        blog.status = 'rejected'
        blog.save()

        # Create or update rejection reason
        rejection, created = RejectionReason.objects.get_or_create(blog=blog)
        rejection.reason = reason_text
        rejection.save()

        messages.success(request, "Blog has been rejected successfully.")
        return redirect("blog_app:profile", username=blog.author.username)

    return render(request, "blog_app/reject_blog.html", {"blog": blog})








from django.shortcuts import render, get_object_or_404, redirect
from .models import Blog, BlogImage
from .forms import BlogForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    # Allow only the author or an admin to edit
    if request.user != blog.author and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit this blog.")
        return redirect('blog_app:blog_detail', blog_id=blog.id)

    rejection_reason = RejectionReason.objects.filter(blog=blog).last()

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            blog = form.save(commit=False)

            # If blog was rejected and edited, reset status to "pending"
            if blog.status.lower() == "rejected":
                blog.status = "pending"

            blog.save()

            # Handle new images (if uploaded)
            images = request.FILES.getlist('images')
            for image in images:
                BlogImage.objects.create(blog=blog, image=image)

            # Handle removal of selected images
            remove_images = request.POST.getlist('remove_images')
            if remove_images:
                BlogImage.objects.filter(id__in=remove_images, blog=blog).delete()

            messages.success(request, "Blog updated successfully! It is now pending review.")
            return redirect('blog_app:profile', username=blog.author.username)
    else:
        form = BlogForm(instance=blog)

    return render(request, "blog_app/edit_blog.html", {
        "form": form,
        "blog": blog,
        "existing_images": blog.images.all(),
        "rejection_reason": rejection_reason  
    })



from django.contrib.auth.decorators import login_required, user_passes_test
# Check if user is superadmin
def is_superadmin(user):
    return user.is_superuser

@user_passes_test(is_superadmin)  # Only super admin can delete
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    blog.delete()
    return redirect('blog_app:profile', username=blog.author.username)




from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import CustomPasswordResetForm
from .models import CustomUser


User = get_user_model()

from django.utils.timezone import now
from datetime import timedelta

def password_reset_request_view(request):
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            user = User.objects.filter(email=email).first()

            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                user.password_reset_requested_at = now()
                user.password_reset_created_at = now()
                user.save(update_fields=['password_reset_requested_at', 'password_reset_created_at'])

                reset_url = request.build_absolute_uri(
                    reverse('blog_app:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                # Render the email using an HTML template
                email_body = render_to_string('blog_app/password_reset_email.html', {'reset_url': reset_url,'user': user})

                send_mail(
                    subject="Password Reset Request",
                    message="Click the link to reset your password: " + reset_url,  # Fallback plain text
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=email_body  # Send the HTML version
                )

                messages.success(request, "A password reset link has been sent to your email.")
                return redirect('blog_app:password_reset_success')
    else:
        form = CustomPasswordResetForm()

    return render(request, 'blog_app/password_reset_request.html', {'form': form})



from django.utils.timezone import now
from datetime import timedelta
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect

User = get_user_model()

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Invalid reset link.")
        return redirect('blog_app:password_reset')

    # Check token validity
    if not default_token_generator.check_token(user, token):
        messages.error(request, "This reset link is invalid or expired.")
        return redirect('blog_app:password_reset')

    # Check if token is expired (30-minute limit)
    if not user.password_reset_created_at or now() - user.password_reset_created_at > timedelta(minutes=30):
        messages.error(request, "This reset link has expired. Request a new one.")
        return redirect('blog_app:password_reset')

    if request.method == "POST":
        new_password = request.POST['password']
        user.set_password(new_password)
        user.password_reset_created_at = None  # Clear token time after reset
        user.save()
        messages.success(request, "Your password has been reset successfully.")
        return redirect('blog_app:login')

    return render(request, 'blog_app/password_reset_confirm.html', {'validlink': True})



def password_reset_done_view(request):
    return render(request, 'blog_app/password_reset_success.html')


from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings  # ✅ Import settings
from .models import Job
from .forms import JobForm

# Function to check if user is admin
def is_admin(user):
    return user.is_superuser  # ✅ Works with CustomUser

# View to list all jobs
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'blog_app/job_list.html', {'jobs': jobs})

# View to add a job (Only Admin)
@login_required
@user_passes_test(is_admin)
def add_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user  # ✅ Uses CustomUser
            job.save()
            return redirect('blog_app:job_list')  # Redirect to job list page
    else:
        form = JobForm()
    return render(request, 'blog_app/add_job.html', {'form': form})




# View to edit a job (Only Admin)
@login_required
@user_passes_test(is_admin)
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            return redirect('blog_app:job_list')  # Redirect to job list page
    else:
        form = JobForm(instance=job)
    return render(request, 'blog_app/edit_job.html', {'form': form, 'job': job})

# View to delete a job (Only Admin)
@login_required
@user_passes_test(is_admin)
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        job.delete()
        return redirect('blog_app:job_list')  # Redirect to job list page
    return render(request, 'blog_app/delete_job.html', {'job': job})


# def contact(request):
#     return render(request, 'blog_app/contact.html')



from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm  # Import your form
from .models import ContactMessage  # Import your model (create if it doesn't exist)

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the form data manually to the database
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message']
            )

            # Optionally send an email (if configured)
             # Send email
            send_mail(
                subject=form.cleaned_data['subject'],
                message=f"Name: {form.cleaned_data['name']}\n"
                        f"Email: {form.cleaned_data['email']}\n"
                        f"Email: {form.cleaned_data['subject']}\n"
                        f"Message: {form.cleaned_data['message']}",
                from_email=form.cleaned_data['email'],
                recipient_list=['saikumarbhogadi9@gmail.com'],
                fail_silently=False,
            )

            return redirect('blog_app:index')  # Redirect after submission

    else:
        form = ContactForm()

    return render(request, "blog_app/contact.html", {"form": form})





from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .forms import JobApplicationForm
from .models import JobApplication, Job

def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)  # Fetch the job based on job_id

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)  # Don't save yet
            application.job = job  # Assign the selected job
            application.save()

            # ✅ Send email notification to HR
            hr_email = "saikumarbhogadi9@gmail.com"  # Update with your HR email
            subject = f"New Job Application for {job.title}"
            message = f"""
            A new job application has been submitted.

            Job Title: {job.title}
            Applicant Name: {application.name}
            Mobile: {application.mobile}
            Email: {application.email}
            Experience: {application.experience}
            Description: {application.description}
            Status: {application.status}

            Please review the application in the admin panel.
            """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [hr_email])

            return redirect('blog_app:job_list')  # Redirect after submission

    else:
        form = JobApplicationForm()

    return render(request, 'blog_app/apply_job.html', {'form': form, 'job': job})



from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import JobApplication

# Function to check if the user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff  # Only admin users can access

@login_required
@user_passes_test(is_admin)  # Restricts access to admin users only
def admin_job_applications(request):
    applications = JobApplication.objects.all().order_by('-applied_at')
    return render(request, 'blog_app/admin_applications.html', {'applications': applications})

@login_required
@user_passes_test(is_admin)  # Restricts access to admin users only
def update_application_status(request, app_id, status):
    application = get_object_or_404(JobApplication, id=app_id)
    
    if status in ['Approved', 'Rejected']:
        application.status = status
        application.save()

    return redirect(reverse('blog_app:admin_job_applications'))

