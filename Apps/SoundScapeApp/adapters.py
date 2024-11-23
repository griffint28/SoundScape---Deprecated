from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect

class CustomAccountAdapter(DefaultAccountAdapter):
    def post_login(self, request, user, *args, **kwargs):
        """
        Redirect the user to connect their Spotify account after logging in.
        """
        if not hasattr(user, 'spotifytoken'):  #Check if Spotify is already linked
            return redirect('spotify_login')  #Redirect to Spotify OAuth
        return super().post_login(request, user, *args, **kwargs)
