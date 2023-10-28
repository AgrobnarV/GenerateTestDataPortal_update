from datetime import datetime

from flask import Flask, render_template, request
from loguru import logger

from api import backend_methods as task
from utils.other_funcs import date_now, sleep_timer

# create the Flask app
app = Flask(__name__)


@logger.catch
@app.route('/')
def index():
    return render_template('index.html')


@logger.catch
@app.route('/create_tasks_first_service')
def first_service_create_tasks_sock():
    return render_template('first_service_create_tasks.html')


@logger.catch
@app.route('/create_tasks_second_service')
def second_service_create_tasks_sock():
    return render_template('second_service_create_tasks.html')


@logger.catch
@app.route('/create_tasks_third_service')
def third_service_create_tasks_sock():
    return render_template('third_service_create_tasks.html')


@logger.catch
@app.route('/create_tasks_forth_service')
def forth_service_create_tasks_sock():
    return render_template('forth_service_create_tasks.html')


@logger.catch
@app.route('/create_barcode')
def carriage_barcode_sock():
    return render_template('create_barcode.html')


@logger.catch
@app.route('/load_route_list')
def load_route_list_sock():
    return render_template('load_route_list.html')


@logger.catch
@app.route('/update_priority_attribute')
def update_priority_attribute_sock():
    return render_template('priority_attributes.html')


@logger.catch
@app.route('/add_other_priority')
def route_article_attribute_add():
    return render_template('other_attributes.html')


@logger.catch
@app.route('/receipt_creating')
def receipt_creating_rout():
    return render_template('create_receipt.html')


@logger.catch
@app.route('/create_route_lists')
def create_route_lists():
    _id = request.args.get('ids', '')
    if '-' in _id:
        _id = _id.split('-')[1]
    return task.load_route_list(_id)


@logger.catch
@app.route('/add_other_priority')
def add_other_priority():
    box_ids = request.args.get('box_ids', '').split(',')
    attrs = {
        "Type 1": request.args.get('Type 1'),
        "Type 2": request.args.get('Type 2'),
        "Type 3": request.args.get('Type 3'),
        "Type 4": request.args.get('Type 4'),
        "Type 5": request.args.get('Type 5')
    }
    attributes = list(
        map(
            lambda x: True if x == 'true' else False,
            attrs.values()
        )
    )
    if len(box_ids) > 0 and any(attributes):
        return task.add_other_priority(box_ids, attrs)
    else:
        return (
            f"Wrong format type box_ids={request.args.get('box_ids', '')}, "
            f"attrs={attrs}",
            400
        )


@logger.catch
@app.route('/create_tasks_first_service')
def update_first_service_create_tasks():
    date_time = date_now()
    client_id = request.args.get('client_id', "")
    local_warehouse_id = request.args.get('local_warehouse_id', "")
    type_id = request.args.get('type_id', "")
    client_name = request.args.get('client_name', "")
    longitude = request.args.get('longitude', "")
    latitude = request.args.get('latitude', "")
    address = request.args.get('address', "")
    boxes_count = int(request.args.get('boxes_count', ""))
    if client_id == "":
        return "Enter the client_id", 400

    boxes = task.update_first_service_create_tasks(
        boxes_count=boxes_count,
        local_warehouse_id=int(local_warehouse_id),
        delivery_variant_id=int(type_id),
        client_name=client_name,
        latitude=latitude,
        longitude=longitude,
        address=address
    )
    boxes_list = boxes["boxes"]
    sleep_timer(2)
    moving_boxes = task.change_status_for_boxes(boxes_list, local_warehouse_id)
    sleep_timer(2)
    route_list = task.create_route_lists(
        client_id,
        boxes_list,
        date_time,
        local_warehouse_id
    )
    if route_list["status"] != 201:
        return f"{route_list}", 400
    sleep_timer(7)
    give_out = task.short_giveout_route_lists(
        boxes_list, route_list["RouteListId"],
        local_warehouse_id
    )
    if give_out["status"] != 200:
        return {
            "responses": {
                "boxes": boxes,
                "moving_boxes": moving_boxes,
                "route_list": route_list
            },
            "give_out": give_out
        }, 400
    logger.debug({
        "responses": {
            "boxes": boxes,
            "moving_boxes": moving_boxes,
            "route_list": route_list,
            "give_out": give_out
        }
    })
    return {
        "boxes_id": ', '.join(str(x) for x in boxes_list)
    }


@logger.catch
@app.route('/create_tasks_second_service')
def create_tasks_second_service():
    date_time = date_now()
    boxes_list = []
    client = request.args.get('client', '')
    local_warehouse_id = request.args.get('local_warehouse_id', '')
    payment_type = request.args.get('payment_type', '')
    type_id = request.args.get('type_id', '')
    boxes_count = int(request.args.get('boxes_count', ''))
    if client == "":
        return "Enter the client_id", 400
    timeslot_response = task.get_time_ranges(
        type_id=int(type_id)
    )
    timeslot = timeslot_response["timeSlots"]

    logger.debug(
        f"{client}, "
        f"{local_warehouse_id}, "
        f"{type_id}, "
        f"{boxes_count}, "
        f"{timeslot}"
    )
    create_tasks_second_service_responses = []
    moving_boxes_responses = []
    for _ in range(boxes_count):
        box = task.create_tasks_second_service(
            type_id=type_id, timeslot_id=timeslot,
            payment_type=payment_type
        )
        if box["status"] != 201:
            return f"{box}", 400
        sleep_timer(2)
        create_tasks_second_service_responses.append(box)
        moving_boxes_responses.append(
            task.change_status_for_box(str(box["boxId"]), int(local_warehouse_id))
        )
        boxes_list.append(str(box["boxId"]))
    sleep_timer(3)
    route_list = task.create_route_lists(
        client, boxes_list, date_time, local_warehouse_id
    )
    sleep_timer(5)
    give_out = task.short_giveout_route_lists(
        boxes_list, route_list["RouteListId"],
        local_warehouse_id
    )
    if give_out["status"] != 200:
        return {
            "responses": {
                "timeslot": timeslot_response,
                "create_tasks_second_service": create_tasks_second_service_responses,
                "moving_boxes": moving_boxes_responses,
                "route_list": route_list
            },
            "give_out": give_out
        }, 400
    logger.debug({
        "responses": {
            "timeslot": timeslot_response,
            "create_tasks_second_service": create_tasks_second_service_responses,
            "moving_boxes": moving_boxes_responses,
            "route_list": route_list,
            "give_out": give_out
        }
    })
    return {
        "box_id": boxes_list
    }


@logger.catch
@app.route('/create_barcode')
def create_barcode():
    global boxes, boxes_response, add_boxes_to_special_boxes, special_box, append_boxes_to_special_boxes
    cartoons_count = int(request.args.get('count', ''))
    boxes_count = int(request.args.get('boxes_count', ''))
    route_id = int(request.args.get('route_id', ''))
    local_warehouse_id = int(request.args.get('local_warehouse_id', ''))
    type_id = int(request.args.get('type_id', ''))
    boxes_name = ()
    date_time = datetime.now()
    date_time = date_time.strftime("%Y-%m-%dT00:00:00")
    new_special_box = task.create_special_boxes(route_id, date_time)
    if new_special_box["status"] == 201:
        new_special_box = new_special_box["special_box"]
    else:
        return f"{new_special_box}", 400
    if cartoons_count > 0:
        sleep_timer(2)
        boxes = task.create_tasks_third_service(
            box_count=cartoons_count, local_warehouse_id=local_warehouse_id,
            type_id=type_id
        )
        boxes_response = []
        for box in boxes["box"]:
            special_box = task.create_pallets(new_special_box)
            if special_box["status"] != 200:
                return f"{special_box}", 400
            box_name = task.get_boxes_name(box)
            if box_name["status"] == 200:
                box_name = box_name["names"]
            else:
                return f"{special_box}", 400
            boxes_response.append([special_box, box_name])
            boxes_name.append(box_name['box']['name'])
        logger.debug(boxes_name)
        sleep_timer(6)
        add_boxes_to_special_boxes = task.add_boxes_to_special_boxes(
            new_special_box,
            boxes_name
        )
    if boxes_count > 0:
        special_box = task.create_tasks_third_service(
            boxes_count=boxes_count, local_warehouse_id=local_warehouse_id,
            type_id=type_id
        )
        sleep_timer(2)
        append_boxes_to_special_boxes = task.get_boxes_within_special_boxes(
            special_box["box"], new_special_box
        )
        sleep_timer(3)
    approve_special_box = task.approve_special_boxes_into_warehouse(new_special_box)
    new_special_box = f"%1%{str(new_special_box)[:12]}"
    logger.debug({
        "barcode": new_special_box,
        "responses": {
            "new_special_box": new_special_box,
            "boxes": boxes or "",
            "boxes_response": boxes_response or "",
            "add_boxes_to_special_boxes": add_boxes_to_special_boxes or "",
            "special_box": special_box or "",
            "append_boxes_to_special_boxes": append_boxes_to_special_boxes or "",
            "approve_special_box": approve_special_box,
        }
    })
    return new_special_box


@logger.catch
@app.route('/forth_service_create_tasks')
def create_tasks_forth_service():
    global append_boxes
    date_time = date_now()
    cartoons_list = []
    client_id = request.args.get('client_id', '')
    local_warehouse_id = request.args.get('local_warehouse_id', '')
    type_id = request.args.get('type_id', '')
    warehouse_place_id = int(request.args.get('warehouse_place_id', ''))
    boxes_count = int(request.args.get('box_count', ""))
    if client_id == "":
        return "Enter the client id", 400
    box = task.create_tasks_forth_service(
        boxes_count=boxes_count,
        local_warehouse_id=int(local_warehouse_id),
        type_id=int(type_id),
    )
    if box["status"] != 201:
        return f"{box}", 400
    boxes_list = box["box"]
    logger.debug(boxes_list)
    sleep_timer(2)
    article_boxes = task.create_pallets_boxes(local_warehouse_id, warehouse_place_id)

    if article_boxes["status"] != 201:
        return f"{article_boxes}", 400
    sleep_timer(2)
    for box in boxes_list:
        append_boxes = task.append_boxes_to_special_boxes(
            box, article_boxes["article_boxes"]
        )
        if append_boxes["status"] != 201:
            return f"{append_boxes}", 400
    sleep_timer(2)
    articles_state = task.change_special_boxes_state(article_boxes["article_boxes"])
    sleep_timer(2)
    moving_boxes_response = task.change_status_for_box(
        article_boxes["article_boxes"],
        int(local_warehouse_id)
    )
    if articles_state["status"] != 200:
        return f"{article_boxes}", 400
    logger.debug(request.args.get('add_boxes'))
    logger.debug(request.args.get('add_boxes') == "true")

    boxes_response = []
    moving_boxes_response = []
    if request.args.get('add_boxes') == "true":
        box = task.create_tasks_forth_service(
            boxes_count=1, local_warehouse_id=int(local_warehouse_id),
            type_id=int(type_id)
        )
        if box["status"] != 201:
            return f"{box}", 400
        sleep_timer(2)
        boxes_response.append(box)
        moving_boxes_response.append(
            task.change_status_for_box(
                str(box["box"][0]), int(local_warehouse_id)
            )
        )
        cartoons_list.append(str(box["cartoon"][0]))
        boxes_list.append(str(box["box"][0]))
    sleep_timer(5)
    route_list = task.create_route_lists(
        client_id, boxes_list, date_time, local_warehouse_id
    )
    if route_list["status"] != 201:
        return f"{route_list}", 400
    sleep_timer(5)
    cartoons_list.append(str(article_boxes["article_boxes"]))

    give_out = task.short_giveout_route_lists(
        cartoons_list, route_list["RouteListId"],
        local_warehouse_id
    )
    if give_out["status"] != 200:
        return f"{give_out}", 400
    logger.debug({
        "responses": {
            "box": box,
            "article_boxes": article_boxes,
            "append_boxes": append_boxes,
            "articles_state": articles_state,
            "moving_boxes_response": moving_boxes_response,
            "boxes_response": boxes_response,
            "route_list": route_list,
            "give_out": give_out
        }
    })
    return {
        "box_id": boxes_list
    }


@logger.catch
@app.route('/update_priority_attribute')
def update_priority_attribute():
    box_id = request.args.get('box_id', '')
    priority = request.args.get('priority', '')
    if box_id == "":
        return "Enter box id", 400
    box_name = task.get_boxes_name(
        box_id)["names"]['box']['name']
    return task.update_priority_attribute(box_name, priority)


@logger.catch
@app.route('/forth_service_create_tasks')
def create_tasks_forth_service():
    global append_postings
    date_time = date_now()
    cartoon_list = []
    client_id = request.args.get('client_id', '')
    local_warehouse_id = request.args.get('local_warehouse_id', '')
    type_id = request.args.get('type_id', '')
    warehouse_place_id = int(request.args.get('warehouse_place_id', ''))
    box_count = int(request.args.get('box_count', ""))
    if client_id == "":
        return "Enter the client id", 400
    box_id = task.create_tasks_forth_service(
        boxes_count=box_count,
        local_warehouse_id=int(local_warehouse_id),
        type_id=int(type_id),
    )
    if box_id["status"] != 201:
        return f"{box_id}", 400
    boxes_list = box_id["box_id"]
    logger.debug(boxes_list)
    article_boxes = task.create_pallets_boxes(local_warehouse_id, warehouse_place_id)

    if article_boxes["status"] != 201:
        return f"{article_boxes}", 400
    sleep_timer(2)
    for box_id in boxes_list:
        append_postings = task.append_boxes_to_special_boxes(
            box_id, article_boxes["article_boxes"]
        )
        if append_postings["status"] != 201:
            return f"{append_postings}", 400
    sleep_timer(2)
    articles_state = task.change_special_boxes_state(article_boxes["article_boxes"])
    sleep_timer(2)
    moving_box_response = task.change_status_for_box(
        article_boxes["article_boxes"],
        int(local_warehouse_id)
    )
    if articles_state["status"] != 200:
        return f"{article_boxes}", 400
    logger.debug(request.args.get('add_box'))
    logger.debug(request.args.get('add_box') == "true")

    boxes_response = []
    moving_boxes_response = []
    if request.args.get('add_box') == "true":
        box_id = task.create_tasks_forth_service(
            boxes_count=1, local_warehouse_id=int(local_warehouse_id),
            type_id=int(type_id)
        )
        if box_id["status"] != 201:
            return f"{box_id}", 400
        sleep_timer(2)
        boxes_response.append(box_id)
        moving_boxes_response.append(
            task.change_status_for_box(
                str(box_id["box_id"][0]), int(local_warehouse_id)
            )
        )
        cartoon_list.append(str(box_id["box_id"][0]))
        boxes_list.append(box_id["box_id"][0])
    sleep_timer(3)
    route_list = task.create_route_lists(
        client_id, boxes_list, date_time, local_warehouse_id
    )
    if route_list["status"] != 201:
        return f"{route_list}", 400
    sleep_timer(3)
    cartoon_list.append(str(article_boxes["article_boxes"]))

    logger.debug({
        "responses": {
            "box_id": box_id,
            "article_boxes": article_boxes,
            "append_postings": append_postings,
            "articles_state": articles_state,
            "moving_box_response": moving_box_response,
            "boxes_response": boxes_response,
            "moving_boxes_response": moving_boxes_response,
            "route_list": route_list
        }
    })
    return {
        "Result": task.load_route_list(route_list["RouteListId"]),
        "Boxes list": boxes_list
    }


@logger.catch
@app.route('/receipt_creating')
def receipt_creating():
    payment_id = request.args.get('payment_id', '')
    receipt_id = request.args.get('receipt_id', '')
    created_date = request.args.get('created_date', '')
    updated_date = request.args.get('updated_date', '')
    done_date = request.args.get('done_date', '')
    salary_type = request.args.get('salary_type', '')
    payment_body = request.args.get('payment_body', '')
    receipt_link = request.args.get('receipt_link', '')
    cancellation_date = request.args.get('cancellation_date', '')
    if not payment_id:
        return "Enter PaymentID", 400
    if not receipt_id:
        return "Enter ReceiptID", 400
    if not created_date:
        return "Enter created_date", 400
    if not updated_date:
        return "Enter updated_date", 400
    if not done_date:
        return "Enter done_date", 400
    if not salary_type:
        return "Enter salary_type", 400
    if not payment_body:
        return "Enter payment_body", 400
    return task.receipt_creating(
        payment_id,
        receipt_id,
        created_date,
        updated_date,
        done_date,
        salary_type,
        payment_body,
        receipt_link,
        cancellation_date,
    )


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=8888, host='1.1.1.1')
