from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Location, SystemARecord, SystemBEntry
from .services.comparator import reconcile_records


def health(request):
    return JsonResponse({'status': 'ok'})


@require_GET
def tenant_list(request):
    tenants = list(Location.objects.values('org_id').distinct().order_by('org_id'))
    return JsonResponse({'results': tenants})


@require_GET
def discrepancy_list(request):
    org_id = (request.GET.get('org_id') or '').strip()
    reason = (request.GET.get('reason') or 'ALL').strip().upper()

    if not org_id:
        return JsonResponse({'error': 'org_id query parameter is required'}, status=400)

    location_map = dict(Location.objects.values_list('location_id', 'org_id'))
    a_rows = list(SystemARecord.objects.values())
    b_rows = list(SystemBEntry.objects.values())
    results = reconcile_records(a_rows, b_rows, location_map)

    # Security boundary: tenant filtering happens before serialization.
    tenant_results = [r for r in results if r.org_id == org_id]
    if reason != 'ALL':
        tenant_results = [r for r in tenant_results if r.reason == reason]

    # Server-side sort is deterministic and keeps the UI simple.
    sort = (request.GET.get('sort') or 'asc').lower()
    def numeric_key(item):
        raw = item.val_a if item.val_a not in (None, '') else item.val_b
        try:
            from .services.comparator import safe_decimal
            parsed = safe_decimal(raw)
            return (parsed is None, parsed or 0)
        except Exception:
            return (True, 0)
    tenant_results.sort(key=numeric_key, reverse=sort == 'desc')

    return JsonResponse({
        'org_id': org_id,
        'count': len(tenant_results),
        'results': [r.to_dict() for r in tenant_results],
    })
