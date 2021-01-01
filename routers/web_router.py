from flask.json import jsonify
from werkzeug.utils import escape, unescape
from utils.image_util import ImageUtil
from flask_wtf import file
from utils.forms_util import DeleteItemForm, FilterForm, NewCommentForm, NewItemForm, EditItemForm
from flask.helpers import flash, send_from_directory
from utils.db_util import DBUtily
from flask import render_template, request, redirect, url_for
from app import app
from flask_wtf.file import FileRequired
import traceback

@app.route("/")
def home():
    conn = DBUtily.get_db()
    cur = conn.cursor()

    form = FilterForm(request.args, meta={"csrf": False})

    categories = DBUtily.get_categories()
    categories.insert(0, (0, "---"))
    form.category.choices = categories

    subcategories = DBUtily.get_subcategories()
    subcategories.insert(0, (0, "---"))
    form.subcategory.choices = subcategories

    query = """select i.id, i.title, i.description, i.price, i.image, c.name, s.name 
                                from items as i
                                inner join categories as c on i.category_id = c.id
                                inner join subcategories as s on i.subcategory_id = s.id"""


    if form.validate():
        filter_queries = []
        parameters = []
        
        if form.title.data.strip():
            filter_queries.append("i.title like ?")
            parameters.append("%" + escape(form.title.data) + "%")

        if form.title.data.strip():
            filter_queries.append("i.category_id = ?")
            parameters.append(form.category.data)

        if form.title.data.strip():
            filter_queries.append("i.subcategory_id = ?")
            parameters.append(form.subcategory.data)
        
        if filter_queries:
            query += " WHERE "
            query += " AND ".join(filter_queries)
        
        if form.price.data:
            if form.price.data == 1:
                query += " order by i.price DESC"
            else:
                query += " order by i.price"
        else:
            items_from_db = cur.execute(query+" order by i.id DESC")

        items_from_db = cur.execute(query, tuple(parameters))
   
    else:
        items_from_db = cur.execute(query+" order by i.id DESC")

    items = []
    for row in items_from_db:
        item = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "price": row[3],
            "image": row[4],
            "category": row[5],
            "subcategory": row[6]
        }
        items.append(item)
    return render_template("home.html", items=items, form=form)

@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(app.config["IMAGE_UPLOADS"], filename)

@app.route("/item/new", methods=["GET", "POST"])
def new_item(): 
    conn = DBUtily.get_db()
    cur = conn.cursor()
   
    form = NewItemForm()
   
    form.category.choices = DBUtily.get_categories()
    form.subcategory.choices = DBUtily.get_subcategories()
        
    if form.validate_on_submit() and form.image.validate(form, extra_validators=[FileRequired()],):
        
        filename = ImageUtil.save_image(form.image)

        cur.execute("""INSERT INTO items
                        (title, description, price, image, category_id, subcategory_id) 
                        VALUES(?, ?, ?, ?, ?, ?)""",
                    (
                        escape(form.title.data),
                        escape(form.description.data),
                        float(form.price.data),
                        filename,
                        form.category.data,
                        form.subcategory.data
                    )    
                )
        conn.commit()
        flash("Item {} has been successfully submitted.".format(request.form.get("title")), "success")
        return redirect(url_for("home"))

    return render_template("new_item.html", form=form)

@app.route("/item/<int:item_id>")
def item(item_id):
    conn = DBUtily.get_db()
    cur = conn.cursor()
    cur.execute("""select i.id, i.title, i.description, i.price, i.image, c.name, s.name 
                    from items as i
                    inner join categories as c on i.category_id = c.id
                    inner join subcategories as s on i.subcategory_id = s.id
                    where i.id = ?""",
                    (item_id,)
                )
    row = cur.fetchone()
    try:
        item = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "price": row[3],
            "image": row[4],
            "category": row[5],
            "subcategory": row[6]
        }

        comments = []
        if item:
            comments_from_db = DBUtily.get_comments_by_item_id(item_id)
            for row in comments_from_db:
                comment = {
                    "content": row[0]
                }
                comments.append(comment)
        
        commentForm = NewCommentForm()
        commentForm.item_id.data = item_id
        deleteItemForm = DeleteItemForm()
        return render_template("item.html", item=item, comments=comments, commentForm=commentForm, deleteItemForm=deleteItemForm)
    except Exception:
        traceback.print_exc()
        return redirect(url_for("home"))

@app.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
def edit_item(item_id):
    conn = DBUtily.get_db()
    cur = conn.cursor()

    item = DBUtily.check_if_item_exists(item_id)

    if item:
        form = EditItemForm()
        if form.validate_on_submit():
            
            filename = item["image"]
            if form.image.data:
                filename = ImageUtil.save_image(form.image)

            cur.execute("update items set title = ?, description = ?, price = ?, image = ? where id = ?",
                            (
                                escape(form.title.data),
                                escape((form.description.data)),
                                float(form.price.data),
                                filename,
                                item_id
                            )
            )
            conn.commit()
            flash("Item {} has been successfully updated.".format(request.form.get("title")), "success")
            return redirect(url_for("item", item_id=item_id))

        form.title.data = unescape(item["title"])
        form.description.data = unescape(item["description"])
        form.price.data = item["price"]
        
        return render_template("edit_item.html", item=item, form=form)

    return redirect(url_for("home"))                   

@app.route("/item/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    conn = DBUtily.get_db()
    cur = conn.cursor()

    item = DBUtily.check_if_item_exists(item_id)

    # delete item if exists
    if item:
        cur.execute("delete from items where id = ?", (item_id,))
        conn.commit()
        flash("Item {} has been successfully deleted.".format(item["title"]), "success")
    else:
        flash("This item doesn't exist.", "danger")
    
    return redirect(url_for("home"))
    
@app.route("/category/<int:category_id>")
def category(category_id):
    subcategories = DBUtily.get_subcategory_by_category_id(category_id)
    return jsonify(subcategories=subcategories)

@app.route("/comment/new", methods=["POST"])
def new_comment():
    form = NewCommentForm()
    if form.validate_on_submit():
        DBUtily.add_new_comment(escape(form.content.data), form.item_id.data)
    return redirect(url_for("item", item_id=form.item_id.data))
