from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    get_operator,
    )
from netmanager.security import AuthenticationPolicy, AuthorizationPolicy
from pyramid.session import SignedCookieSessionFactory

from .models import get_operator

def operator(request):
    if "operator_call" in request.session:
        o = get_operator(request.session['operator_call'])
        if o.active:
            return o
        else:
            del request.session['operator_call']
    return False


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    sf = SignedCookieSessionFactory(settings["session_key"], timeout=None)
    config.set_session_factory(sf)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_renderer(".html", "pyramid_jinja2.renderer_factory")
    authn_policy = AuthenticationPolicy()
    authz_policy = AuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_request_method(operator, reify=True)
    config.add_route('index', '/')
    config.add_route('view_net', '/view_net/{id}')
    config.add_route('signin', '/signin')
    config.add_route('signout', '/signout')
    config.add_route('settings_index', '/settings')
    config.add_route('settings_chpw', '/settings/chpw')
    config.add_route('settings_basic', '/settings/basic')
    config.add_route('operators', '/operators')
    config.add_route('operators_add', '/operators/add')
    config.add_route('operators_edit', '/operators/edit/{call}')
    config.add_route('operators_save', '/operators/save/{call}')
    config.add_route('operators_del', '/operators/del/{call}')
    config.add_route('operators_lastlocation', '/operators/last/{call}')
    config.add_route('activitylog', '/activitylog')
    config.add_route('nets', '/nets')
    config.add_route('nets_add', '/nets/add')
    config.add_route('nets_del', '/nets/del/{id}')
    config.add_route('nets_console', '/nets/console/{id}')
    config.add_route('nets_begin', '/nets/begin/{id}')
    config.add_route('nets_close', '/nets/close/{id}')
    config.add_route('nets_reopen', '/nets/reopen/{id}')
    config.add_route('nets_checkin', '/nets/checkin/{id}')
    config.add_route('nets_checkin_ack', '/nets/checkin_ack/{id}/{checkin_id}')
    config.add_route('nets_checkin_deack', '/nets/checkin_deack/{id}/{checkin_id}')
    config.add_route('nets_checkin_save', '/nets/checkin_save/{id}/{checkin_id}')
    config.add_route('nets_checkin_del', '/nets/checkin_del/{id}/{checkin_id}')
    config.add_route('nets_checkin_report', '/nets/checkin_report/{checkin_id}')
    config.add_route('reports', '/reports')
    config.add_route('chart_operator_activity', '/reports/chart_operator_activity')
    config.add_route('chart_net_participation', '/reports/chart_net_participation')
    config.scan()
    return config.make_wsgi_app()
