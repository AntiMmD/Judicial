from django.shortcuts import render


def index(request):
    """Main documentation page."""
    return render(request, 'docs/index.html')


def accounts_api(request):
    """Accounts API documentation."""
    return render(request, 'docs/accounts.html')


def job_api(request):
    """Properties API documentation."""
    return render(request, 'docs/jobs.html')


def search_api(request):
    """Search API documentation."""
    return render(request, 'docs/search.html')


def setup_guide(request):
    """Setup guide for frontend developers."""
    return render(request, 'docs/setup-guide.html')


def project_structure(request):
    """Project structure and design patterns documentation."""
    return render(request, 'docs/project-structure.html')
