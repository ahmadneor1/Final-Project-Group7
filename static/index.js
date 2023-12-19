function logout() {
    $.cookie('mytoken');
    $.removeCookie('mytoken', { path: '/', expires: 1, sameSite: 'None', secure: true });
    alert('You have been logged out!');
    window.location.href = '/login';
}