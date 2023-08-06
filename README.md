# Music Review Project

Fully functional music review webpage built using Python, Flask, PSQL, and runs on Google Cloud VM.

Home Page: 
- Top reviews: displays reviews with the most likes in the database 
- Searchbar for artists/albums: search for albums or artists (case sensitive). 
- List of artists and albums: explore the artist/album information and reviews in a streamlined manner.

Dashboard Page:
- User information: user info retrieved from sign up form, excluding the password
- User reviews: all previously left reviews, empty if no reviews yet
- User playlist: albums added to the playlist, empty if playlist hasn't been created 

Final implementation features -- Users can:
- Write a review for any album of their choice
- Like other users’ reviews at most once. If they attempt to like more times, they are rerouted to a page that states they have attempted to like the review more than once.
- Search for Artists and Albums. If the artist/album searched for is not in the database, webpage will notify the user to try again. If the search was successful, then the user will be routed to the page for that particular artist/album
- Create and view a personal playlist containing albums on the user's Dashboard page
- Edit their personal playlist and add more Albums if they wish. One caveat, however, is that users are only able to create one playlist and are unable to delete added Albums. For any given user in our database, they can have at most one playlist.
- Browse a “Most Popular/Top Reviews” section on the main home page. These reviews are the top 3 most liked reviews and updates when the rankings change.
- Navigate to an Artist's page and view artist information, including released albums
- Navigate to an Album's page and view more information about it. Album reviews are found on this page. 
- Sign in or sign up. No user can access the data, especially the reviews about an album, without an account.
- Logout of account. Have the option to Log back in.

