from source import db
from source.main.model.users import Users
from source.main.model.locations import Locations
from source.main.model.userPhotos import UserPhotos
from source.main.model.commentPhotos import CommentPhotos
from source.main.model.postComments import PostComments
from source.main.model.messages import Messages
from source.main.model.messagesPhotos import MessagePhotos
from source.main.model.forumPhotos import ForumPhotos
from source.main.model.forumPosts import ForumPosts
from source.main.model.relationships import Relationships
from source.main.model.groups import Groups
from source.main.model.favorite import Favorite
from source.main.model.commentFavorite import CommentFavorite
from source.main.model.provinces import Provinces
from source.main.model.chat1vs1 import Chat1vs1 
if __name__ == "__main__":
    db.create_all()
