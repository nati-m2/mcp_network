from typing import List, Dict, Any

# This module defines a tool that returns a structured UI response
# with many supported element types. It follows the project's pattern
# of exposing a register_tools(mcp) function that FastMCP picks up.


# ---- Element builders (kept small, reusable) ----

def build_text(value: str) -> Dict[str, Any]:
    return {"type": "text", "value": value}


def build_icon(name: str, size: int = 24, color: str | None = None) -> Dict[str, Any]:
    el: Dict[str, Any] = {"type": "icon", "name": name, "size": size}
    if color:
        el["color"] = color
    return el


def build_icon_button(icon: str, color: str | None, tooltip: str | None, action: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    el: Dict[str, Any] = {
        "type": "icon_button",
        "icon": icon,
        "action": action,
    }
    if color:
        el["color"] = color
    if tooltip:
        el["tooltip"] = tooltip
    if payload:
        el["payload"] = payload
    return el


def build_button(label: str, action: str, icon: str | None = None, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    el: Dict[str, Any] = {"type": "button", "label": label, "action": action}
    if icon:
        el["icon"] = icon
    if payload:
        el["payload"] = payload
    return el


def build_form(fields: List[Dict[str, Any]], submit: Dict[str, Any]) -> Dict[str, Any]:
    return {"type": "form", "fields": fields, "submit": submit}


def build_checklist(title: str, style: str, action: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"type": "checklist", "title": title, "style": style, "action": action, "items": items}


def build_alert(level: str, text: str) -> Dict[str, Any]:
    return {"type": "alert", "level": level, "text": text}


def build_chart(title: str | None, chart_type: str, data: List[Dict[str, Any]], collapsible: bool | None = None, on_tap_action: str | None = None) -> Dict[str, Any]:
    el: Dict[str, Any] = {"type": "chart", "chartType": chart_type, "data": data}
    if title is not None:
        el["title"] = title
    if collapsible is not None:
        el["collapsible"] = collapsible
    if on_tap_action is not None:
        el["onTapAction"] = on_tap_action
    return el


def build_tabs(tabs: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"type": "tabs", "tabs": tabs}


def build_carousel(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"type": "carousel", "items": items}


def build_progress(variant: str, value: float, label: str | None = None) -> Dict[str, Any]:
    el: Dict[str, Any] = {"type": "progress", "variant": variant, "value": value}
    if label is not None:
        el["label"] = label
    return el


def build_map(center: Dict[str, float], zoom: int, place_marker_on_tap: bool, on_tap_action: str, markers: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "type": "map",
        "center": center,
        "zoom": zoom,
        "placeMarkerOnTap": place_marker_on_tap,
        "onTapAction": on_tap_action,
        "markers": markers,
    }


def build_markdown(text: str) -> Dict[str, Any]:
    return {"type": "markdown", "text": text}


def build_code(text: str) -> Dict[str, Any]:
    return {"type": "code", "text": text}


def build_media(media_type: str, url: str, caption: str | None = None) -> Dict[str, Any]:
    el: Dict[str, Any] = {"type": "media", "mediaType": media_type, "url": url}
    if caption:
        el["caption"] = caption
    return el


def build_chips(items: List[Dict[str, Any]], multi_select: bool, action: str | None = None) -> Dict[str, Any]:
    el: Dict[str, Any] = {"type": "chips", "items": items, "multiSelect": multi_select}
    if action:
        el["action"] = action
    return el


def build_date_picker(label: str, action: str) -> Dict[str, Any]:
    return {"type": "date_picker", "label": label, "action": action}


def build_time_picker(label: str, action: str) -> Dict[str, Any]:
    return {"type": "time_picker", "label": label, "action": action}


def build_modal(label: str, on_close_action: str | None, content: List[Dict[str, Any]]) -> Dict[str, Any]:
    el: Dict[str, Any] = {"type": "modal", "label": label, "content": content}
    if on_close_action:
        el["onCloseAction"] = on_close_action
    return el


def build_cards(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"type": "cards", "items": items}


def build_table(columns: List[str], rows: List[List[Any]]) -> Dict[str, Any]:
    return {"type": "table", "columns": columns, "rows": rows}


# ---- Tool registration ----

def register_tools(mcp):
    """Register UI elements tool with FastMCP."""

    @mcp.tool()
    def get_ui_elements(types: list[str] | None = None, elements_spec: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        """
        החזר תגובת UI במבנה {"type":"response","elements":[...]}

        פרמטרים:
        - types: רשימת סוגי אלמנטים להכללה (למשל: ["alert", "button"]). אם לא סופק, יוחזר הסט המלא.
        - elements_spec: רשימת מפרטים דינמיים ליצירת אלמנטים בפועל. כל מפרט כולל לפחות שדה "type" ופרמטרים רלוונטיים.
                         כאשר מסופק, האלמנטים יורכבו מהקלט במקום הדמו.
        """
        elements: List[Dict[str, Any]] = []

        # --- helper: build from a single spec dict ---
        def build_from_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
            t = spec.get("type")
            if not t:
                return build_alert("error", "Spec חסר שדה type")
            match t:
                case "text":
                    return build_text(spec.get("value", ""))
                case "icon":
                    return build_icon(
                        name=spec.get("name", "info"),
                        size=int(spec.get("size", 24)),
                        color=spec.get("color"),
                    )
                case "icon_button":
                    return build_icon_button(
                        icon=spec.get("icon", "info"),
                        color=spec.get("color"),
                        tooltip=spec.get("tooltip"),
                        action=spec.get("action", "noop"),
                        payload=spec.get("payload"),
                    )
                case "button":
                    return build_button(
                        label=spec.get("label", "לחץ"),
                        action=spec.get("action", "noop"),
                        icon=spec.get("icon"),
                        payload=spec.get("payload"),
                    )
                case "form":
                    return build_form(
                        fields=spec.get("fields", []),
                        submit=spec.get("submit", {"label": "שליחה", "action": "submit"}),
                    )
                case "checklist":
                    return build_checklist(
                        title=spec.get("title", "רשימה"),
                        style=spec.get("style", "checkbox"),
                        action=spec.get("action", "checklist_changed"),
                        items=spec.get("items", []),
                    )
                case "alert":
                    return build_alert(level=spec.get("level", "info"), text=spec.get("text", ""))
                case "chart":
                    return build_chart(
                        title=spec.get("title"),
                        chart_type=spec.get("chartType", "bar"),
                        data=spec.get("data", []),
                        collapsible=spec.get("collapsible"),
                        on_tap_action=spec.get("onTapAction"),
                    )
                case "tabs":
                    return build_tabs(spec.get("tabs", []))
                case "carousel":
                    return build_carousel(spec.get("items", []))
                case "progress":
                    return build_progress(
                        variant=spec.get("variant", "linear"),
                        value=float(spec.get("value", 0.0)),
                        label=spec.get("label"),
                    )
                case "map":
                    return build_map(
                        center=spec.get("center", {"lat": 0.0, "lng": 0.0}),
                        zoom=int(spec.get("zoom", 10)),
                        place_marker_on_tap=bool(spec.get("placeMarkerOnTap", False)),
                        on_tap_action=spec.get("onTapAction", "map_tap"),
                        markers=spec.get("markers", []),
                    )
                case "markdown":
                    return build_markdown(spec.get("text", ""))
                case "code":
                    return build_code(spec.get("text", ""))
                case "media":
                    return build_media(
                        media_type=spec.get("mediaType", "image"),
                        url=spec.get("url", ""),
                        caption=spec.get("caption"),
                    )
                case "chips":
                    return build_chips(
                        items=spec.get("items", []),
                        multi_select=bool(spec.get("multiSelect", False)),
                        action=spec.get("action"),
                    )
                case "date_picker":
                    return build_date_picker(label=spec.get("label", "בחר תאריך"), action=spec.get("action", "date_picked"))
                case "time_picker":
                    return build_time_picker(label=spec.get("label", "בחר שעה"), action=spec.get("action", "time_picked"))
                case "modal":
                    return build_modal(
                        label=spec.get("label", "מודל"),
                        on_close_action=spec.get("onCloseAction"),
                        content=spec.get("content", []),
                    )
                case "cards":
                    return build_cards(spec.get("items", []))
                case "table":
                    return build_table(columns=spec.get("columns", []), rows=spec.get("rows", []))
                case _:
                    return build_alert("warning", f"סוג אלמנט לא נתמך: {t}")

        # If elements_spec provided, build dynamically
        if elements_spec:
            elements = [build_from_spec(s) for s in elements_spec]
        else:
            # FALLBACK: demo composition (for convenience/testing)
            # basic text
            elements.append(build_text("זהו טקסט לדוגמה המגיע מהקובץ"))

            # icons and buttons
            elements.append(build_icon(name="info", size=28, color="#2080FF"))
            elements.append(build_icon_button(icon="delete", color="#E53935", tooltip="מחיקה", action="delete_item", payload={"id": 123}))
            elements.append(build_button(label="עריכה", icon="edit", action="edit_item", payload={"id": 123}))

        if not elements_spec:
            # form
            elements.append(build_form(
                fields=[
                    {"key": "name",  "label": "שם",     "type": "text",      "required": True,  "hint": "שם מלא"},
                    {"key": "email", "label": "אימייל",  "type": "email",     "required": True},
                    {"key": "notes", "label": "הערות",   "type": "multiline", "required": False},
                ],
                submit={"label": "שליחה", "action": "submit_contact"}
            ))

            # checklist
            elements.append(build_checklist(
                title="משימות",
                style="checkbox",
                action="checklist_changed",
                items=[
                    {"key": "t1", "label": "לסגור באגים",   "checked": True},
                    {"key": "t2", "label": "להוסיף טסטים", "checked": False},
                ]
            ))

            # alert
            elements.append(build_alert(level="success", text="הפעולה הושלמה בהצלחה!"))

            # charts
            elements.append(build_chart(
                title="מכירות לפי חודש",
                chart_type="bar",
                collapsible=True,
                on_tap_action="sales_drilldown",
                data=[
                    {"label": "ינואר", "value": 30},
                    {"label": "פברואר", "value": 70},
                    {"label": "מרץ",   "value": 45},
                ],
            ))
            elements.append(build_chart(
                title=None,
                chart_type="line",
                on_tap_action="trend_drilldown",
                collapsible=None,
                data=[
                    {"label": "Q1", "value": 15},
                    {"label": "Q2", "value": 25},
                    {"label": "Q3", "value": 22},
                    {"label": "Q4", "value": 30},
                ],
            ))

            # tabs
            elements.append(build_tabs([
                {
                    "label": "סקירה",
                    "content": [
                        build_text("ברוכים הבאים"),
                        build_progress(variant="linear", value=0.6, label="התקדמות 60%"),
                    ],
                },
                {
                    "label": "פרטים",
                    "content": [
                        build_table(columns=["Key", "Value"], rows=[["A", "1"], ["B", "2"]]),
                    ],
                },
            ]))

            # carousel
            elements.append(build_carousel([
                {"content": [build_text("כרטיס 1"), build_icon("check")]},
                {"content": [build_text("כרטיס 2"), build_button(label="לעוד", action="more")]},
            ]))

            # progress
            elements.append(build_progress(variant="linear", value=0.35, label="35%"))
            elements.append(build_progress(variant="circular", value=0.8, label="80%"))

            # map
            elements.append(build_map(
                center={"lat": 32.0853, "lng": 34.7818},
                zoom=12,
                place_marker_on_tap=True,
                on_tap_action="map_tap",
                markers=[
                    {"lat": 32.0853,  "lng": 34.7818,  "label": "תל אביב",  "action": "marker_tap", "payload": {"id": 1}},
                    {"lat": 31.77196, "lng": 35.217018, "label": "ירושלים", "action": "marker_tap", "payload": {"id": 2}},
                ],
            ))

            # markdown, code, media
            elements.append(build_markdown("## כותרת\nטקסט עם **הדגשה** ורשימה:\n- פריט 1\n- פריט 2"))
            elements.append(build_code("function add(a,b){ return a+b; }"))
            elements.append(build_media(media_type="image", url="https://picsum.photos/800/400", caption="תמונה לדוגמה"))

            # chips
            elements.append(build_chips(
                items=[
                    {"label": "React",   "value": "react",   "selected": True},
                    {"label": "Flutter", "value": "flutter"},
                    {"label": "Vue",     "value": "vue"},
                ],
                multi_select=True,
                action="chips_changed",
            ))

            # youtube media
            elements.append(build_media(media_type="youtube", url="https://www.youtube.com/embed/tgbNymZ7vqY", caption="וידאו לדוגמה"))

            # date/time pickers
            elements.append(build_date_picker(label="בחר תאריך", action="date_picked"))
            elements.append(build_time_picker(label="בחר שעה", action="time_picked"))

            # modal
            elements.append(build_modal(
                label="פתח מודל",
                on_close_action="modal_closed",
                content=[
                    build_text("זהו תוכן בתוך מודל"),
                    build_button(label="כפתור פנימי", action="modal_inner_click"),
                ],
            ))

            # cards
            elements.append(build_cards([
                {
                    "title": "כרטיס 1",
                    "subtitle": "תיאור קצר",
                    "imageUrl": "https://picsum.photos/seed/card1/900/300",
                    "content": [build_text("תוכן הכרטיס")],
                },
                {
                    "title": "כרטיס 2",
                    "content": [build_button(label="פעולה", action="card_action")],
                },
            ]))

            # table
            elements.append(build_table(columns=["name", "value"], rows=[["A", 12], ["B", 40], ["C", 23]]))

        # filter by requested types if provided
        if types:
            filtered = [el for el in elements if el.get("type") in set(types)]
            # Ensure a valid response even if nothing matched
            if not filtered:
                filtered = [build_alert(level="info", text="לא נמצאו אלמנטים מתאימים לבקשה")]  # graceful fallback
            return {"type": "response", "elements": filtered}

        return {"type": "response", "elements": elements}
