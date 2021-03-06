from typing import List, Union

import flask
from flask_jwt_extended import (jwt_required, get_jwt_identity, jwt_optional)

from src.database import db
from src.models.models import Coffee, User, Review

app = flask.Blueprint('reviews_controller', __name__)


@app.route("/reviews", methods=['GET'])
@jwt_optional
def get_reviews():
    sql_query: List = []
    reviewer_id: Union[int, None] = flask.request.args.get('reviewer',
                                                           type=int)
    bean_ids: Union[str, None] = flask.request.args.get('beans')
    offset: Union[int, None] = flask.request.args.get('offset', type=int)
    bean_ids = bean_ids.split(",") if bean_ids else None
    if reviewer_id:
        user: User = User.query.get(reviewer_id)
        if user is not None:
            sql_query.append(Review.reviewer.has(id=reviewer_id))
    if bean_ids:
        bean_query = []
        for bean_id in bean_ids:
            bean_query.append(Review.coffee.has(bean_id=bean_id))
        sql_query.append(db.or_(*bean_query))
    if offset is None:
        offset = 0
    reviews: List[Review] = Review.query.filter(
        db.and_(*sql_query)).order_by(db.desc(Review.created_at))\
        .limit(10).offset(offset).all()
    review_exist_more: Union[Review, None] = Review.query.filter(
        db.and_(*sql_query)).order_by(db.desc(
            Review.created_at)).limit(1).offset(offset + 10).one_or_none()
    exist_more: bool = review_exist_more is not None
    return flask.jsonify({
        "result":
        True,
        "data":
        [review.to_json(with_user=get_jwt_identity()) for review in reviews],
        "existMore":
        exist_more
    })


@app.route("/reviews/<int:id>", methods=['GET'])
@jwt_optional
def get_review(id: int):
    review: Review = Review.query.get(id)
    return flask.jsonify({
        "result": True,
        "data": review.to_json(with_user=get_jwt_identity())
    })


@app.route("/reviews/<int:id>", methods=['PUT'])
@jwt_required
def update_review(id):
    current_user: User = User.query.filter_by(
        name=get_jwt_identity()).one_or_none()
    try:
        form_data = flask.request.json
        if current_user.id != form_data.get('reviewerId'):
            return flask.jsonify({"result": False, "message": "ユーザが不正です"}), 401
        bitterness: float = form_data.get('bitterness')
        coffee_id: int = form_data.get('coffeeId')
        feeling: str = form_data.get('feeling')
        situation: float = form_data.get('situation')
        strongness: float = form_data.get('strongness')
        reviewer_id: int = current_user.id
        want_repeat: float = form_data.get('wantRepeat')

        review: Review = Review.query.get(id)
        coffee: Coffee = Coffee.query.get(coffee_id)
        if review.coffee_id != coffee_id:
            return flask.jsonify({
                "result": False,
                "message": "対象のコーヒーが一致しません"
            })
        if not list(
                filter(lambda drinker: drinker.id == reviewer_id,
                       coffee.drinkers)):
            return flask.jsonify({
                "result": False,
                "message": "このコーヒーへのレビューを書く権利がありません"
            }), 400
        review.bitterness = bitterness
        review.feeling = feeling
        review.situation = situation
        review.strongness = strongness
        review.want_repeat = want_repeat
        if not review.is_valid():
            return flask.jsonify({"result": False, "message": "入力が不正です"})
        db.session.commit()
        return flask.jsonify({
            "result": True,
            "message": "レビューを更新しました。",
            "data": review.to_json()
        })
    except Exception as e:
        print(e)
        return flask.jsonify({
            "result": False,
            "message": f"予期せぬエラーが発生しました : {e}"
        }), 500


@app.route("/reviews", methods=['POST'])
@jwt_required
def create_review():
    current_user = User.query.filter_by(name=get_jwt_identity()).one_or_none()
    try:
        form_data = flask.request.json
        if current_user.id != form_data.get('reviewerId'):
            return flask.jsonify({"result": False, "message": "ユーザが不正です"}), 401
        bitterness: float = form_data.get('bitterness')
        coffee_id: int = form_data.get('coffeeId')
        feeling: str = form_data.get('feeling')
        situation: float = form_data.get('situation')
        strongness: float = form_data.get('strongness')
        reviewer_id: int = current_user.id
        want_repeat: float = form_data.get('wantRepeat')
        new_review = Review(bitterness=bitterness,
                            want_repeat=want_repeat,
                            coffee_id=coffee_id,
                            situation=situation,
                            strongness=strongness,
                            feeling=feeling,
                            reviewer_id=reviewer_id)
        if not new_review.is_valid():
            return flask.jsonify({"result": False, "message": "入力が不正です"}), 400
        coffee: Coffee = Coffee.query.get(coffee_id)
        if not list(
                filter(lambda drinker: drinker.id == reviewer_id,
                       coffee.drinkers)):
            return flask.jsonify({
                "result": False,
                "message": "このコーヒーへのレビューを書く権利がありません"
            })
        if list(filter(lambda r: r.reviewer_id == reviewer_id,
                       coffee.reviews)):
            return flask.jsonify({
                "result": False,
                "message": "このコーヒーにはすでにレビューが書かれています"
            })
        if len(coffee.reviews) >= len(coffee.drinkers):
            return flask.jsonify({
                "result": False,
                "message": "このコーヒーにはすでにレビューが書かれています"
            })
        db.session.add(new_review)
        coffee.reviews.append(new_review)
        db.session.commit()
        return flask.jsonify({
            "result": True,
            "message": "レビューを作成しました。",
            "data": new_review.to_json()
        })
    except Exception as e:
        print(e)
        return flask.jsonify({
            "result": False,
            "message": f"予期せぬエラーが発生しました : {e}"
        }), 500
