import inspect
from django.template.context import RequestContext, Context
print('Context', Context)
print('RequestContext', RequestContext)
print('has copy Context', hasattr(Context, 'copy'))
print('has copy RequestContext', hasattr(RequestContext, 'copy'))
print('has __copy__ Context', hasattr(Context, '__copy__'))
print('has __copy__ RequestContext', hasattr(RequestContext, '__copy__'))
print('Context __copy__ source:')
print(inspect.getsource(Context.__copy__))
print('RequestContext __copy__ source:')
print(inspect.getsource(RequestContext.__copy__))
