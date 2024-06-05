from source import db
from flask import request, make_response, jsonify
from sqlalchemy import or_, and_
from source.main.model.forumPosts import ForumPosts
from source.main.model.forumPhotos import ForumPhotos
from source.main.model.favorite import Favorite
from source.main.model.users import Users
from source.main.extend import *
from source.main.function.postComments import *
from source.main.model.postComments import PostComments
from source.main.model.commentPhotos import CommentPhotos
from datetime import datetime
from sqlalchemy.sql import label, text


def addNewPost(id):
    try:
        if not request.json:
            return make_response(
                jsonify(
                    {"status": 400, "message": "Bad Request - No JSON data provided"}
                ),
                400,
            )

        json_data = request.json

        required_fields = [
            "GroupID",
            "Title",
            "Content",
            "PostLatitude",
            "PostLongitude",
        ]
        for field in required_fields:
            if field not in json_data:
                return make_response(
                    jsonify(
                        {"status": 400, "message": f"Missing required field: {field}"}
                    ),
                    400,
                )

        post = ForumPosts(
            UserID=id,
            GroupID=json_data["GroupID"],
            Title=json_data["Title"],
            Content=json_data["Content"],
            PostTime=datetime.now(),
            IPPosted=request.remote_addr,
            PostLatitude=json_data["PostLatitude"],
            PostLongitude=json_data["PostLongitude"],
        )
        db.session.add(post)
        db.session.commit()

        # Add associated images (PhotoURL) if provided
        if "PhotoURL" in json_data and isinstance(json_data["PhotoURL"], list):
            for url in json_data["PhotoURL"]:
                image_post = ForumPhotos(
                    PostID=post.PostID, PhotoURL=base64ToByte(url), UploadTime=datetime.now()
                )
                db.session.add(image_post)

        db.session.commit()

        # Retrieve and return the newly created post
        post_id = post.PostID
        return viewPost(post_id)

    except Exception as e:
        print(f"Error: {e}")
        error = "An error occurred while creating the post: " + str(e)
        return make_response(jsonify({"status": 500, "message": error}), 500)


def viewPost(id):
    try:
        data = []
        post = ForumPosts.query.get(id)
        post_favorite_count = Favorite.query.filter(
            and_(Favorite.PostID == id, Favorite.FavoriteType == 1)
        ).count()

        if post:
            post_data = {
                "UserID": post.UserID,
                "GroupID": post.GroupID,
                "Content": post.Content,
                "Title": post.Title,
                "PostTime": post.PostTime,
                "IPPosted": post.IPPosted,
                "PostLatitude": post.PostLatitude,
                "PostLongitude": post.PostLongitude,
                "FavoriteNumber": post_favorite_count,
            }

            data.append(post_data)

            images = ForumPhotos.query.filter(ForumPhotos.PostID == post.PostID).all()
            photo_urls = [byteToString(image.PhotoURL) for image in images]

            if photo_urls:
                post_data["PhotoURL"] = photo_urls

            return {"status": 200, "Post": data}
        else:
            return {"status": 404, "message": "Post not found"}

    except Exception as e:
        print(f"Error: {e}")
        error = "An error occurred while viewing the post " + str(e)
        return {"status": 500, "message": error}


def updatePost(PostID):
    try:
        data_json = request.json
        post_need_update = ForumPosts.query.filter(ForumPosts.PostID == PostID).first()

        if post_need_update:
            if "Title" in data_json:
                post_need_update.Title = data_json["Title"]
            if "Content" in data_json:
                post_need_update.Content = data_json["Content"]

            db.session.commit()
            return viewPost(PostID)
        else:
            return make_response(
                jsonify({"Status": 404, "Message": "The post not found!"}), 404
            )

    except Exception as e:
        return make_response(
            jsonify(
                {"status": 500, "message": "An error occurred while updating the post"}
            ),
            500,
        )


def deletePost(PostID):
    try:
        post_need_delete = ForumPosts.query.filter(ForumPosts.PostID == PostID).first()

        if post_need_delete:
            removeFavorite(PostID)
            removeAllComment(PostID)
            db.session.delete(post_need_delete)
            db.session.commit()
            return make_response(
                jsonify({"Status": 200, "Message": "Post has been deleted!"}), 200
            )
        else:
            return make_response(
                jsonify({"Status": 404, "Message": "The post not found!"}), 404
            )

    except Exception as e:
        return make_response(
            jsonify(
                {"status": 500, "message": str(e)}
            ),
            500,
        )


def searchPost(key):
    try:
        posts = (
            ForumPosts.query.filter(
                or_(
                    ForumPosts.Title.ilike(f"%{key}%"),
                    ForumPosts.Content.ilike(f"%{key}%"),
                )
            )
            .order_by(ForumPosts.PostTime.desc())
            .all()
        )

        if posts:
            posts_data = [
                {
                    "PostID": post.PostID,
                    "UserID": post.PostID,
                    "GroupID": post.GroupID,
                    "Title": post.Title,
                    "Content": post.Content,
                    "PostTime": post.PostTime,
                    "IPPosted": post.IPPosted,
                    "PostLatitude": post.PostLatitude,
                    "PostLongitude": post.PostLongitude,
                }
                for post in posts
            ]
            return jsonify({"status": 200, "Posts": posts_data})
        else:
            return make_response(
                jsonify({"status": 404, "Message": "No posts found for the given key"}),
                404,
            )

    except Exception as e:
        return make_response(
            jsonify(
                {
                    "status": 500,
                    "message": "An error occurred while searching for posts",
                }
            ),
            500,
        )


def favoritePost(UserID, PostID):
    try:
        post_favorite = Favorite.query.filter(
            and_(Favorite.UserID == UserID, Favorite.PostID == PostID)
        ).first()

        if post_favorite:
            db.session.delete(post_favorite)
            db.session.commit()
            return make_response(
            jsonify(
                {
                    "status": 200,
                    "message": "Remove Favorite Success",
                }
            ),
            200,
        )
        else:
            new_favorite = Favorite(
                UserID=UserID,
                PostID=PostID,
                FavoriteType=True,
                FavoriteTime=datetime.now(),
            )
            db.session.add(new_favorite)

        db.session.commit()
        return viewPost(PostID)

    except Exception as e:
        return make_response(
            jsonify(
                {
                    "status": 500,
                    "message": "An error occurred while favoriting the post",
                }
            ),
            500,
        )


def removeFavorite(PostID):
    try:
        post = ForumPosts.query.filter_by(PostID=PostID).first()

        if post:
            favorite_to_delete = Favorite.query.filter_by(PostID=PostID).all()

            if favorite_to_delete:
                for favorite in favorite_to_delete:
                    db.session.delete(favorite)

                db.session.commit()

                return make_response(
                    jsonify(
                        {"status": 200, "message": "All Favorite deleted successfully"}
                    ),
                    200,
                )
            else:
                return make_response(
                    jsonify(
                        {"status": 404, "message": "No Favorite found for the comment"}
                    ),
                    404,
                )
        else:
            return make_response(
                jsonify({"status": 404, "message": "Comment not found"}), 404
            )
    except Exception as e:
        print(e)
        return make_response(
            jsonify(
                {"status": 500, "message": "An error occurred while deleting images"}
            ),
            500,
        )


def getListPost(GroupID, PostFrom, PostTo, UserID):
    try:
        offset = (PostFrom - 1) * PostTo
        
        posts = ForumPosts.query.filter(ForumPosts.GroupID == GroupID).order_by(ForumPosts.PostTime.desc()).offset(offset).limit(PostTo).all()
        
        list_post = []
        for post in posts: 
            post_user = Users.query.get(post.UserID)
            post_photo = ForumPhotos.query.filter(ForumPhotos.PostID == post.PostID).first()
            post_first_comment = PostComments.query.filter(PostComments.PostID == post.PostID).first()
            post_favorite = Favorite.query.filter(Favorite.PostID == post.PostID)
            post_favorite_count = post_favorite.count()
            checkUserID = post_favorite.filter(Favorite.UserID == UserID).first()
            isFavorited = checkUserID is not None
            first_comment = {}
            if post_first_comment:
                first_comment_user = Users.query.get(post.UserID)
                comment_photo = CommentPhotos.query.get(post_first_comment.CommentID)
                if comment_photo:
                    first_comment.update({
                        "Content":post_first_comment.Content,
                        "Photo":byteToString(comment_photo.PhotoURL),
                        "UserFullName":first_comment_user.FullName,
                        "Username": first_comment_user.Username,
                        "Avatar": byteToString(first_comment_user.avatarLink),
                        "Time": post_first_comment.CommentTime,
                        "TimeUpdated": post_first_comment.CommentUpdateTime
                    })
                else:
                    first_comment.update({
                        "Content":post_first_comment.Content,
                        "Photo": None,
                        "UserFullName":first_comment_user.FullName,
                        "Username": first_comment_user.Username,
                        "Avatar": byteToString(first_comment_user.avatarLink),
                        "Time": post_first_comment.CommentTime,
                        "TimeUpdated": post_first_comment.CommentUpdateTime
                    })

            list_post.append({
                "PostID": post.PostID,
                "UserID": post.UserID,
                "UserFullName": post_user.FullName,
                "Username": post_user.Username,
                "Avatar": byteToString(post_user.avatarLink),
                "GroupID": post.GroupID,
                "FirstComment":first_comment,
                "Title": post.Title,
                "Content": post.Content,
                "PostTime": post.PostTime,
                "IPPosted": post.IPPosted,
                "PostLatitude": post.PostLatitude,
                "PostLongitude": post.PostLongitude,
                "UpdatePostAt": post.UpdatePostAt,
                "FavoriteCount": post_favorite_count,
                "IsFavorited": isFavorited,
                "Photo": byteToString(post_photo.PhotoURL) if post_photo else None,
            })
        
        return jsonify({'status': 200, 'list_posts': list_post})
    except Exception as e:
        print(e)
        return make_response(jsonify({'status': 500, 'message': 'An error occurred!'+ str(e)}), 500)  