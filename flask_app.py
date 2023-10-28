import os
from datetime import datetime

from flask import Flask, render_template, request, send_from_directory
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
@app.route('/lozon_task')
def first_service_create_tasks_sock():
    return render_template('first_service_create_tasks.html')


@logger.catch
@app.route('/oms_prepay_task')
def second_service_create_tasks_sock():
    return render_template('second_service_create_tasks.html')


@logger.catch
@app.route('/carriage_with_containers')
def carriage_barcode_sock():
    return render_template('create_barcode.html')


@logger.catch
@app.route('/ml_load')
def ml_load():
    return render_template('load_route_list.html')


@logger.catch
@app.route('/delivery_priority')
def delivery_priority():
    return render_template('priority_attributes.html')


@logger.catch
@app.route('/article_boxes_task')
def article_boxes_task():
    return render_template('forth_service_create_tasks.html')


@logger.catch
@app.route('/new_article_boxes_task')
def new_article_boxes_task():
    return render_template('third_service_create_tasks.html')


@logger.catch
@app.route('/route_article_attribute_add')
def route_article_attribute_add():
    return render_template('other_attributes.html')


@logger.catch
@app.route('/receipt_creating')
def receipt_creating_rout():
    return render_template('create_receipt.html')


@logger.catch
@app.route('/create_ml_load')
def create_ml_load():
    _id = request.args.get('ids', '')
    if '-' in _id:
        _id = _id.split('-')[1]
    return task.load_route_list(_id)


@logger.catch
@app.route('/route_set_article_attribute')
def route_set_article_attribute():
    posting_ids = request.args.get('posting_ids', '').split(',')
    attrs = {
        "adult": request.args.get('adult'),
        "alkohole": request.args.get('alkohole'),
        "to_door": request.args.get('to_door'),
        "premium": request.args.get('premium'),
        "jeweler": request.args.get('jeweler')
    }
    attributes = list(
        map(
            lambda x: True if x == 'true' else False,
            attrs.values()
        )
    )
    if len(posting_ids) > 0 and any(attributes):
        return task.add_other_priority(posting_ids, attrs)
    else:
        return (
            f"Неверный формат данных posting_ids={request.args.get('posting_ids', '')}, "
            f"attrs={attrs}",
            400
        )


@logger.catch
@app.route('/lozon_delivery')
def lozon_delivery():
    date_time = date_now()
    postings_list = []
    courier = request.args.get('courier', "")
    start_place_id = request.args.get('start_place_id', "")
    delivery_variant_id = request.args.get('delivery_variant_id', "")
    client_name = request.args.get('client_name', "")
    longitude = request.args.get('longitude', "")
    latitude = request.args.get('latitude', "")
    address = request.args.get('address', "")
    posting_count = int(request.args.get('posting_count', ""))
    scan_it = request.args.get('scanit') == "true"
    if courier == "":
        return "Заполните курьера", 400

    posting = task.update_first_service_create_tasks(
        boxes_count=posting_count,
        local_warehouse_id=int(start_place_id),
        delivery_variant_id=int(delivery_variant_id),
        scan_it=scan_it,
        client_name=client_name,
        latitude=latitude,
        longitude=longitude,
        address=address
    )
    postings_list = posting["posting"]
    sleep_timer(2)
    moving_postings = task.change_status_for_boxes(postings_list, start_place_id)
    sleep_timer(2)
    route_sheet = task.create_route_lists(
        courier,
        postings_list,
        date_time,
        start_place_id
    )
    if route_sheet["status"] != 201:
        return f"{route_sheet}", 400
    sleep_timer(7)
    give_out = task.short_giveout_route_lists(
        postings_list, route_sheet["lozonRouteSheetId"],
        route_sheet["trolizonRouteSheetId"],
        start_place_id
    )
    if give_out["status"] != 200:
        return {
            "responses": {
                "posting": posting,
                "moving_postings": moving_postings,
                "route_sheet": route_sheet
            },
            "give_out": give_out
        }, 400
    logger.debug({
        "responses": {
            "posting": posting,
            "moving_postings": moving_postings,
            "route_sheet": route_sheet,
            "give_out": give_out
        }
    })
    return {
        "posting_id": ', '.join(str(x) for x in postings_list),
        "route_sheet_id": route_sheet["trolizonRouteSheetId"]
    }


@logger.catch
@app.route('/oms_prepay_delivery')
def oms_prepay_delivery():
    date_time = date_now()
    postings_list = []
    courier = request.args.get('courier', '')
    start_place_id = request.args.get('start_place_id', '')
    payment_type = request.args.get('payment_type', '')
    delivery_variant_id = request.args.get('delivery_variant_id', '')
    posting_count = int(request.args.get('posting_count', ''))
    if courier == "":
        return "Заполните курьера", 400
    timeslot_response = task.get_time_ranges(
        delivery_variants_id=int(delivery_variant_id)
    )
    timeslot = timeslot_response["timeSlots"]

    logger.debug(
        f"{courier}, "
        f"{start_place_id}, "
        f"{delivery_variant_id}, "
        f"{posting_count}, "
        f"{timeslot}"
    )
    create_posting_oms_responses = []
    moving_posting_responses = []
    for _ in range(posting_count):
        posting = task.create_tasks_second_service(
            delivery_variant_id=delivery_variant_id, timeslot_id=timeslot,
            payment_type=payment_type
        )
        if posting["status"] != 201:
            return f"{posting}", 400
        sleep_timer(2)
        create_posting_oms_responses.append(posting)
        moving_posting_responses.append(
            task.change_status_for_box(str(posting["postingId"]), int(start_place_id))
        )
        postings_list.append(str(posting["postingId"]))
    sleep_timer(3)
    route_sheet = task.create_route_lists(
        courier, postings_list, date_time, start_place_id
    )
    sleep_timer(5)
    give_out = task.short_giveout_route_lists(
        postings_list, route_sheet["lozonRouteSheetId"],
        route_sheet["trolizonRouteSheetId"],
        start_place_id
    )
    if give_out["status"] != 200:
        return {
            "responses": {
                "timeslot": timeslot_response,
                "create_posting_oms": create_posting_oms_responses,
                "moving_posting": moving_posting_responses,
                "route_sheet": route_sheet
            },
            "give_out": give_out
        }, 400
    logger.debug({
        "responses": {
            "timeslot": timeslot_response,
            "create_posting_oms": create_posting_oms_responses,
            "moving_posting": moving_posting_responses,
            "route_sheet": route_sheet,
            "give_out": give_out
        }
    })
    return {
        "posting_id": postings_list,
        "route_sheet_id": route_sheet["trolizonRouteSheetId"]
    }


@logger.catch
@app.route('/create_carriage_with_containers')
def create_carriage_with_containers():
    containers_count = int(request.args.get('count', ''))
    postings_count = int(request.args.get('postings_count', ''))
    route = int(request.args.get('route', ''))
    start_place_id = int(request.args.get('start_place_id', ''))
    delivery_variant_id = int(request.args.get('delivery_variant_id', ''))
    postings_name = []
    date_time = datetime.now()
    date_time = date_time.strftime("%Y-%m-%dT00:00:00")
    new_carriage = task.create_special_boxes(route, date_time)
    postings = None
    postings_reponses = None
    add_posting_to_carriage = None
    postings_carriage = None
    append_postings_to_carriages = None
    if new_carriage["status"] == 201:
        new_carriage = new_carriage["carriage"]
    else:
        return f"{new_carriage}", 400
    if containers_count > 0:
        sleep_timer(2)
        postings = task.create_tasks_third_service(
            posting_count=containers_count, start_place_id=start_place_id,
            delivery_variant_id=delivery_variant_id
        )
        postings_reponses = []
        for posting in postings["posting"]:
            container = task.create_pallets(new_carriage)
            if container["status"] != 200:
                return f"{container}", 400
            posting_name = task.get_boxes_name(posting)
            if posting_name["status"] == 200:
                posting_name = posting_name["names"]
            else:
                return f"{container}", 400
            postings_reponses.append([container, posting_name])
            postings_name.append(posting_name['posting']['name'])
        logger.debug(postings_name)
        sleep_timer(6)
        add_posting_to_carriage = task.add_boxes_to_special_boxes(
            new_carriage,
            postings_name
        )
    if postings_count > 0:
        postings_carriage = task.create_tasks_third_service(
            posting_count=postings_count, start_place_id=start_place_id,
            delivery_variant_id=delivery_variant_id
        )
        sleep_timer(2)
        append_postings_to_carriages = task.get_boxes_within_special_boxes(
            postings_carriage["posting"], new_carriage
        )
        sleep_timer(3)
    approve_carriage = task.approve_special_boxes_into_warehouse(new_carriage)
    new_carriage = f"%303%{str(new_carriage)[:12]}"
    logger.debug({
        "barcode": new_carriage,
        "responses": {
            "new_carriage": new_carriage,
            "postings": postings or "",
            "postings_reponses": postings_reponses or "",
            "add_posting_to_carriage": add_posting_to_carriage or "",
            "postings_carriage": postings_carriage or "",
            "append_postings_to_carriages": append_postings_to_carriages or "",
            "approve_carriage": approve_carriage,
        }
    })
    return new_carriage


@logger.catch
@app.route('/article_boxes_delivery')
def article_boxes_delivery():
    date_time = date_now()
    containers_list = []
    courier = request.args.get('courier', '')
    start_place_id = request.args.get('start_place_id', '')
    delivery_variant_id = request.args.get('delivery_variant_id', '')
    dst_place_id = int(request.args.get('dst_place_id', ''))
    posting_count = int(request.args.get('posting_count', ""))
    scan_it_in_article_box = request.args.get('scan_it_in_article_box') == "true"
    if courier == "":
        return "Заполните курьера", 400
    posting = task.create_tasks_first_service(
        boxes_count=posting_count,
        start_place_id=int(start_place_id),
        type_id=int(delivery_variant_id),
        scan_it=scan_it_in_article_box
    )
    if posting["status"] != 201:
        return f"{posting}", 400
    postings_list = posting["posting"]
    logger.debug(postings_list)
    sleep_timer(2)
    article_boxes = task.create_pallets_boxes(start_place_id, dst_place_id)

    if article_boxes["status"] != 201:
        return f"{article_boxes}", 400
    sleep_timer(2)
    # append_postings = task.append_postings_to_containers(
    #     posting_id, article_boxes["article_boxes"]
    # )
    # if append_postings["status"] != 201:
    #     return f"{append_postings}", 400
    for posting in postings_list:
        append_postings = task.append_boxes_to_special_boxes(
            posting, article_boxes["article_boxes"]
        )
        if append_postings["status"] != 201:
            return f"{append_postings}", 400
    sleep_timer(2)
    articles_state = task.change_special_boxes_state(article_boxes["article_boxes"])
    sleep_timer(2)
    moving_posting_reposne = task.change_status_for_box(
        article_boxes["article_boxes"],
        int(start_place_id)
    )
    if articles_state["status"] != 200:
        return f"{article_boxes}", 400
    # postings_list = [posting_id]
    logger.debug(request.args.get('add_posting'))
    logger.debug(request.args.get('add_posting') == "true")

    postings_reponses = []
    moving_posting_reponses = []
    if request.args.get('add_posting') == "true":
        posting = task.create_tasks_first_service(
            boxes_count=1, start_place_id=int(start_place_id),
            type_id=int(delivery_variant_id)
        )
        if posting["status"] != 201:
            return f"{posting}", 400
        sleep_timer(2)
        postings_reponses.append(posting)
        moving_posting_reponses.append(
            task.change_status_for_box(
                str(posting["posting"][0]), int(start_place_id)
            )
        )
        containers_list.append(str(posting["posting"][0]))
        postings_list.append(str(posting["posting"][0]))
    logger.debug(request.args.get('scan_it'))
    logger.debug(request.args.get('scan_it') == "true")
    if request.args.get('scan_it') == "true":
        posting = task.create_tasks_first_service(
            boxes_count=1, start_place_id=int(start_place_id),
            type_id=int(delivery_variant_id), scan_it=True
        )
        if posting["status"] != 201:
            return f"{posting}", 400
        sleep_timer(2)
        postings_reponses.append(posting)
        moving_posting_reponses.append(
            task.change_status_for_box(
                str(posting["posting"][0]), int(start_place_id)
            )
        )
        containers_list.append(str(posting["posting"][0]))
        postings_list.append(str(posting["posting"][0]))
    sleep_timer(5)
    route_sheet = task.create_route_lists(
        courier, postings_list, date_time, start_place_id
    )
    if route_sheet["status"] != 201:
        return f"{route_sheet}", 400
    sleep_timer(5)
    containers_list.append(str(article_boxes["article_boxes"]))

    give_out = task.short_giveout_route_lists(
        containers_list, route_sheet["lozonRouteSheetId"],
        route_sheet["trolizonRouteSheetId"],
        start_place_id
    )
    if give_out["status"] != 200:
        return f"{give_out}", 400
    logger.debug({
        "responses": {
            "posting": posting,
            "article_boxes": article_boxes,
            "append_postings": append_postings,
            "articles_state": articles_state,
            "moving_posting_reposne": moving_posting_reposne,
            "postings_reponses": postings_reponses,
            "moving_posting_reponses": moving_posting_reponses,
            "route_sheet": route_sheet,
            "give_out": give_out
        }
    })
    return {
        "posting_id": postings_list,
        "route_sheet_id": route_sheet["trolizonRouteSheetId"]
    }


@logger.catch
@app.route('/set_delivery_priority')
def set_delivery_priority():
    posting_id = request.args.get('posting_id', '')
    priority = request.args.get('priority', '')
    if posting_id == "":
        return "Введите ID постинга", 400
    posting_name = task.get_boxes_name(
        posting_id)["names"]['posting']['name']
    return task.update_priority_attribute(posting_name, priority)


@logger.catch
@app.route('/new_article_boxes_delivery')
def new_article_boxes_delivery():
    date_time = date_now()
    containers_list = []
    courier = request.args.get('courier', '')
    start_place_id = request.args.get('start_place_id', '')
    delivery_variant_id = request.args.get('delivery_variant_id', '')
    dst_place_id = int(request.args.get('dst_place_id', ''))
    posting_count = int(request.args.get('posting_count', ""))
    scan_it_in_article_box = request.args.get('scan_it_in_article_box') == "true"
    if courier == "":
        return "Заполните курьера", 400
    posting = task.create_tasks_first_service(
        boxes_count=posting_count,
        start_place_id=int(start_place_id),
        type_id=int(delivery_variant_id),
        scan_it=scan_it_in_article_box
    )
    if posting["status"] != 201:
        return f"{posting}", 400
    postings_list = posting["posting"]
    logger.debug(postings_list)
    article_boxes = task.create_pallets_boxes(start_place_id, dst_place_id)

    if article_boxes["status"] != 201:
        return f"{article_boxes}", 400
    sleep_timer(2)
    for posting in postings_list:
        append_postings = task.append_boxes_to_special_boxes(
            posting, article_boxes["article_boxes"]
        )
        if append_postings["status"] != 201:
            return f"{append_postings}", 400
    sleep_timer(2)
    articles_state = task.change_special_boxes_state(article_boxes["article_boxes"])
    sleep_timer(2)
    moving_posting_reposne = task.change_status_for_box(
        article_boxes["article_boxes"],
        int(start_place_id)
    )
    if articles_state["status"] != 200:
        return f"{article_boxes}", 400
    logger.debug(request.args.get('add_posting'))
    logger.debug(request.args.get('add_posting') == "true")

    postings_reponses = []
    moving_posting_reponses = []
    if request.args.get('add_posting') == "true":
        posting = task.create_tasks_first_service(
            boxes_count=1, start_place_id=int(start_place_id),
            type_id=int(delivery_variant_id)
        )
        if posting["status"] != 201:
            return f"{posting}", 400
        sleep_timer(2)
        postings_reponses.append(posting)
        moving_posting_reponses.append(
            task.change_status_for_box(
                str(posting["posting"][0]), int(start_place_id)
            )
        )
        containers_list.append(str(posting["posting"][0]))
        postings_list.append(posting["posting"][0])
    logger.debug(request.args.get('scan_it'))
    logger.debug(request.args.get('scan_it') == "true")
    if request.args.get('scan_it') == "true":
        posting = task.create_tasks_first_service(
            boxes_count=1, start_place_id=int(start_place_id),
            type_id=int(delivery_variant_id), scan_it=True
        )
        if posting["status"] != 201:
            return f"{posting}", 400
        sleep_timer(2)
        postings_reponses.append(posting)
        moving_posting_reponses.append(
            task.change_status_for_box(
                str(posting["posting"][0]), int(start_place_id)
            )
        )
        containers_list.append(str(posting["posting"][0]))
        postings_list.append(posting["posting"][0])
    sleep_timer(3)
    route_sheet = task.create_route_lists(
        courier, postings_list, date_time, start_place_id
    )
    if route_sheet["status"] != 201:
        return f"{route_sheet}", 400
    sleep_timer(3)
    containers_list.append(str(article_boxes["article_boxes"]))

    logger.debug({
        "responses": {
            "posting": posting,
            "article_boxes": article_boxes,
            "append_postings": append_postings,
            "articles_state": articles_state,
            "moving_posting_reposne": moving_posting_reposne,
            "postings_reponses": postings_reponses,
            "moving_posting_reponses": moving_posting_reponses,
            "route_sheet": route_sheet
        }
    })
    return {
        "Результат": task.load_route_list(route_sheet["trolizonRouteSheetId"]),
        "Список постингов": postings_list
    }


@logger.catch
@app.route('/receipt_creating_api')
def receipt_creating_api():
    paymentId = request.args.get('paymentId', '')
    smzInn = request.args.get('smzInn', '')
    receiptId = request.args.get('receiptId', '')
    createdAt = request.args.get('createdAt', '')
    updatedAt = request.args.get('updatedAt', '')
    operationDate = request.args.get('operationDate', '')
    customerType = request.args.get('customerType', '')
    positions = request.args.get('positions', '')
    receiptLink = request.args.get('receiptLink', '')
    cancellationDate = request.args.get('cancellationDate', '')
    if not paymentId:
        return "Введите paymentId", 400
    if not smzInn:
        return "Введите smzInn", 400
    if not receiptId:
        return "Введите receiptId", 400
    if not createdAt:
        return "Введите createdAt", 400
    if not updatedAt:
        return "Введите updatedAt", 400
    if not operationDate:
        return "Введите operationDate", 400
    if not customerType:
        return "Введите customerType", 400
    if not positions:
        return "Введите positions", 400
    return task.receipt_creating(
        paymentId,
        smzInn,
        receiptId,
        createdAt,
        updatedAt,
        operationDate,
        customerType,
        positions,
        receiptLink,
        cancellationDate,
    )


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000, host='0.0.0.0')
