import base64
import datetime
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from pydoc import describe

import jinja2

from app import config, crud, models, schemas
from app.schemas.enums import EventTypeEnum

# ------------------------------------------------------------------------------------------------------
# USEFUL EMAIL HELPERS
# ------------------------------------------------------------------------------------------------------


def format_kv_table(dic: dict):
    res = """<table style="border-collapse: separate; border-spacing: 1em 0.5em;">"""
    res += "".join(
        [
            f"""
        <tr>
            <td style="vertical-align: top;"><b>{ k }:</b></td>
            <td>{ dic[k] }</td>
        </tr>
    """
            for k in dic
        ]
    )
    res += "</table>"
    return res


def format_image(src: str, alt: str):
    """todo: not supported by all email clients."""
    # <h1>image test #1</h1>
    # <div class="email_img_container">
    #     <img src="{src}" alt="{alt}" width="500" height="280" class="email_img">
    # </div>

    # <h1>image test #2</h1>
    # <img src="{src}" alt="{alt}" width="500" height="280">

    # <h1>image test #3</h1>
    # # .... used

    # <h1>image test #4</h1>
    # <table width="50%">
    #     <tr><td>
    #         <img src="{src}" alt="{alt}" width="500"  style="text-align: right; width: 207px; border: 0; text-decoration:none; vertical-align: baseline;">
    #     </td></tr>
    # </table>
    return f"""
    <center>
        <table border="0" cellpadding="0" cellspacing="0" height="100%" width="100%" id="bodyTable">
    <center>
    <tr><td>
        <table border="0" cellpadding="0" cellspacing="0" width="600">
        

                <tr>
                    <td align="center" valign="top" id="bodyCell">
        
        
        <!-- BEGIN TEMPLATE // -->

            <img src="{src}" alt="{alt}" width="500" height="280">

            </td></tr>
            </table>
            </center>
        
        <!-- // END TEMPLATE -->

                </td><!-- /#bodyCell -->
            </tr>
        </table><!-- /#bodyTable -->
    </center>
    """


def format_date(date: datetime):
    return date.strftime("%m/%d/%Y") if date else None


def format_newline_text(text: str):
    return text.replace("\n", "<br/>") if text else None


def format_user_name(db, user_id: int):
    user = crud.user.get(db, user_id)
    return f"{user.name} ({user.email})" if user else None


def format_user_names(db, user_ids: list[int]):
    users = crud.user.get_all(db, user_ids)
    return ",\n".join([f"{u.name} ({u.email})" for u in users]) if users else None


def format_action_status(status: int):
    if status == schemas.enums.StatusEnum.OPEN:
        return "Open"
    elif status == schemas.enums.StatusEnum.ON_HOLD:
        return "On Hold"
    elif status == schemas.enums.StatusEnum.CLOSED:
        return "Closed"
    return None


def format_action_priority(priority: int):
    if priority == schemas.enums.PriorityEnum.LOW:
        return "Low"
    elif priority == schemas.enums.PriorityEnum.MEDIUM:
        return "Medium"
    elif priority == schemas.enums.PriorityEnum.HIGH:
        return "High"
    return None


def format_privacy(privacy: int):
    if privacy == schemas.enums.PrivacyEnum.PUBLIC:
        return "Public"
    elif privacy == schemas.enums.PrivacyEnum.CONFIDENTIAL:
        return "Confidential"
    elif privacy == schemas.enums.PrivacyEnum.REQUESTED:
        return "Requested"
    elif privacy == schemas.enums.PrivacyEnum.DECLINED:
        return "Declined"
    return None


def get_recipients_from_comment(comment):
    mentions = []
    EMAIL_SLUG = "@fmgl.com.au"
    for word in comment.split():
        if word.startswith("@"):
            mentions.append(f"{word[1:]}{EMAIL_SLUG}")

    # remove duplicates
    mentions = list(dict.fromkeys(mentions))

    return mentions


# ------------------------------------------------------------------------------------------------------


def send_email(
    html, subject, recipeints, attachments=[], custom_attachment_names=[], embed_img_path=None
):
    SMTP_HOST = "localrelay.fmg.local"
    SMTP_PORT = 25
    SMTP_USER = "noreply.dep@fmgl.com.au"

    # sanity check
    if len(attachments) != len(custom_attachment_names):
        raise Exception("Attachments and custom attachment names must be the same length")

    # handle single recipient
    if type(recipeints) != list:
        recipeints = [recipeints]

    if config.DEV_MODE:
        print(f"\n\n\nEmail would sent to {recipeints}\n\n\n")
        # test code to export email in a html file
        with open("test.html", "w") as f:
            f.write(html)
        return False

    if config.ENV != "prod":
        subject = f"({config.ENV}) - {subject}"
        if config.USER_WHITELIST:
            recipeints = [r for r in recipeints if r in config.USER_WHITELIST]
        # return False  # turn off emails for non prod (for now)

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(recipeints)
        msg["Subject"] = subject

        # -----------------------------

        # handle embed image
        if embed_img_path:
            fp = open(embed_img_path, "rb")
            img = MIMEImage(fp.read())
            fp.close()
            img.add_header("Content-ID", "<{}>".format("image.png"))
            msg.attach(img)

        # -----------------------------

        msg.attach(MIMEText(html, "html"))

        # -----------------------------

        for ii in range(len(attachments)):
            f = attachments[ii]
            with open(f, "rb") as fp:
                part = MIMEApplication(fp.read(), Name=basename(f))

            # After the file is closed
            part["Content-Disposition"] = (
                'attachment; filename="%s"' % custom_attachment_names[ii]
                if ii < len(custom_attachment_names)
                else basename(f)
            )
            msg.attach(part)

        # -----------------------------

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            print(f"\n\n\nSuccessfully sent to {recipeints}\n\n\n")
            server.sendmail(SMTP_USER, recipeints, msg.as_string())
    except Exception as e:
        print(f"\n\n\nFailed to send to {recipeints}\n\n\n")
        print(e)
        return False


# ---------------------------------------------------


def action_email(db, recipient, subject, header, action):
    def construct_email_description(db, action):
        """ """
        from app import schemas

        owner_texts = []
        for id in action.owner_ids:
            _user = crud.user.get(db, id)
            owner_texts.append(f"{_user.name} ({_user.email})")

        data = {
            "Assigned To": ", ".join(owner_texts) or "NA",
            "Members": format_newline_text(format_user_names(db, action.member_ids)) or "NA",
            "Supervisor": format_user_name(db, action.supervisor_id) or "NA",
            "Status": format_action_status(action.status) or "NA",
            "Priority": format_action_priority(action.priority) or "NA",
            "Due Date": format_date(action.date_due) or "NA",
        }

        description = f"<h3>{action.title}</h3>"
        description += f"<p>{action.description}</p>"

        description += format_kv_table(data)

        description += f"<p><a href='https://{config.SERVER_NAME}/actions?action_id={action.id}'>Please open link to review the action.</a></p>"

        return description

    # -----------------------------------------------------

    templateLoader = jinja2.FileSystemLoader(os.path.join("/app/app/email/templates"))
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template("header_description.html")
    html = templ.render(header=header, description=construct_email_description(db, action))

    send_email(html, subject, recipient)


# -------------------------------------------------------------------------------------------


def investigation_email(db, recipient, subject, header, investigation):
    def construct_email_description(db, action):
        """ """
        from app import schemas

        owner_texts = []
        for id in investigation.owner_ids:
            _user = crud.user.get(db, id)
            owner_texts.append(f"{_user.name} ({_user.email})")

        supervisor = crud.user.get(db, investigation.supervisor_id)
        supervisor = f"{_user.name} ({_user.email})"

        status = "Open"
        if action.status == schemas.enums.StatusEnum.OPEN:
            status = "Open"
        elif action.status == schemas.enums.StatusEnum.ON_HOLD:
            status = "On Hold"
        elif action.status == schemas.enums.StatusEnum.CLOSED:
            status = "Closed"

        data = {
            "Owners": ", ".join(owner_texts) or "NA",
            "Supervisor": supervisor or "NA",
            "Status": status or "NA",
            "Priority": investigation.priority.value or "NA",
        }
        description = f"<h3>{investigation.title}</h3>"
        description += f"<p>{investigation.description}</p>"
        description += format_kv_table(data)

        description += f"<p><a href='https://{config.SERVER_NAME}/investigation?id={investigation.id}'>Please open link to review the investigation.</a></p>"

        return description

    # -------------------------------------------------------------

    templateLoader = jinja2.FileSystemLoader(os.path.join("/app/app/email/templates"))
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template("header_description.html")
    html = templ.render(header=header, description=construct_email_description(db, investigation))

    send_email(html, subject, recipient)


# ---------------------------------------------------


def feedback_email(db, recipient, subject, header, feedback):
    def construct_email_description(db, feedback):
        """ """
        from app import schemas

        # setup
        _owner = crud.user.get(db, feedback.created_by_id)

        reason = "Bug"
        if feedback.reason == schemas.enums.FeedbackReason.BUG:
            reason = "Bug"
        elif feedback.reason == schemas.enums.FeedbackReason.GENERAL_FEEDBACK:
            reason = "General Feedback"

        status = "Open"
        if feedback.status == schemas.enums.FeedbackStatusEnum.OPEN:
            status = "Open"
        elif feedback.status == schemas.enums.FeedbackStatusEnum.ON_HOLD:
            status = "On Hold"
        elif feedback.status == schemas.enums.FeedbackStatusEnum.CLOSED_COMPLETE:
            status = "Closed (Complete)"
        elif feedback.status == schemas.enums.FeedbackStatusEnum.CLOSED_DUPLICATE:
            status = "Closed (Duplicate)"
        elif feedback.status == schemas.enums.FeedbackStatusEnum.CLOSED_FEEDBACK_ONLY:
            status = "Closed (Feedback Only)"

        description = f"<h4>Page Description</h4><p>{feedback.page}</p>"
        description += f"<h4>Summary</h4><p>{feedback.summary}</p>"
        description += f"<h4>How to Replicate</h4><p>{feedback.replicate}</p>"
        description += f"<b>Feedback Type</b>: {reason} <br/>"
        description += f"<b>Created By</b>: {_owner.name} ({_owner.email}) <br/>"
        description += f"<b>Status</b>: {status} <br/>"
        description += f"<p><a href='https://{config.SERVER_NAME}/feedback?id={feedback.id}'>Please open link to review the feedback item.</a></p>"

        return description

    # -----------------------------------------------------

    templateLoader = jinja2.FileSystemLoader(os.path.join("/app/app/email/templates"))
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template("header_description.html")
    html = templ.render(header=header, description=construct_email_description(db, feedback))

    send_email(html, subject, recipient)


# -------------------------------------------------------------------------------------------


def flash_report_distribution(
    recipients, message: str, context, attachments, custom_attachment_names=[]
):
    def business_impact_html(context):
        business_impact_str = ""
        event_duration = context["total_event_duration"] if context["total_event_duration"] else 0.0
        if context["event_type"] == EventTypeEnum.APLUS:
            total_effective_duration = (
                context["total_effective_duration"] if context["total_effective_duration"] else 0.0
            )
            total_tonnes_lost = (
                context["total_tonnes_lost"] if context["total_tonnes_lost"] else 0.0
            )
            business_impact_str += f"Event had an Effective Duration of {total_effective_duration} hours and {round(total_tonnes_lost)} tonnes. "
        elif context["event_type"] == EventTypeEnum.REMS:
            business_impact_str += f"Event lasted {round(event_duration,1)} hours"

        if context["business_impact"]:
            business_impact_str += f"\n{context['business_impact']}"

        return f"<p>{business_impact_str}</p>"

    def root_cause_html(root_causes):
        list_items = [f"<li>{x}</li>" for x in root_causes]
        return f"<ol type='1'>{''.join(list_items)}</ol>"

    site_info = f"""
        <h3>{context['title']}</h3>
        <p>{context['description']}</p>

        {format_image(context["image"], context['equipment_description'])}
        
        <table style='border-collapse: separate;border-spacing: 1em 0.5em;'>
            <tr>
              <td><b>Event Date</b></td>
              <td>{context['event_date']}</td>
            </tr>
            <tr>
              <td><b>Site</b></td>
              <td>{context['site']}</td>
            </tr>
            <tr>
              <td><b>Department</b></td>
              <td>{context['department']}</td>
            </tr>
            <tr>
              <td><b>Functional Location</b></td>
              <td>{context['function_location']}</td>
            </tr>
            <tr>
              <td><b>Equipment</b></td>
              <td>{context['equipment_description']} ({context['object_type']})</td>
            </tr>
            <tr>
              <td><b>Object Part</b></td>
              <td>{context['object_part_description']}</td>
            </tr>
            <tr>
              <td><b>Damage Code</b></td>
              <td>{context['damage_code']}</td>
            </tr>
        </table>
    """

    # handle new line in message
    message = message.replace("\n", "<br/>") if message else ""

    html = f"""
        <p>[auto-generated content below]</p>

        {site_info}
        <hr />

        <h4>Business Impact</h4>
        {business_impact_html(context)}
        <h4>Immediate Action Taken</h4>
        <p>{context['immediate_action_taken']}</p>
        <h4>Root Causes</h4>
        {root_cause_html(context['root_causes'])}

        <p><a href='https://{config.SERVER_NAME}/investigation?id={context['investigation_id']}'>Please open link to revixew the investigation.</a></p>
    """

    # -----------------------------------------------------

    templateLoader = jinja2.FileSystemLoader(os.path.join("/app/app/email/templates"))
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template("header_description.html")
    html = templ.render(header="", description=html)

    # -----------------------------------------------------

    subject = f"Flash Report - {context['title']}"

    # -----------------------------------------------------

    # ? - images embedded in html now, this is no longer required
    # attach flash report image
    # if context["image_path"]:
    #     attachments.append(context["image_path"])
    #     custom_attachment_names.append(f"{context['equipment_description']}.png")

    # -----------------------------------------------------

    send_email(
        html,
        subject,
        recipients,
        attachments,
        custom_attachment_names,
    )


# ---------------------------------------------------


def shared_learning_distribution(
    db, recipients, message: str, context, attachments, custom_attachment_names=[]
):
    def format_actions(actions):
        if not actions:
            return "No Actions."

        res = """<table border="2" style="border-collapse:collapse; border-spacing: 0 10px;">
                    <tr>
                        <th style="text-align: left; padding: 5px;">Title</th>
                        <th style="text-align: left; padding: 5px;">Owner</th>
                        <th style="text-align: left; padding: 5px;">Priority</th>
                        <th style="text-align: left; padding: 5px;">Status</th>
                        <th style="text-align: left; padding: 5px;">Due</th>
                    </tr>
            """

        res += "".join(
            [
                f"""
                    <tr>
                        <td style="padding: 5px;"><a href='https://{config.SERVER_NAME}/actions?action_id={action['id']}' target="_blank">{action['title']}</a></td>
                        <td style="padding: 5px;">{format_user_names(db, action['owner_ids']) if action['owner_ids'] else "NA"}</td>
                        <td style="padding: 5px;">{action['priority'] if action['priority'] else "NA"}</td>
                        <td style="padding: 5px;">{action['status'] if action['status'] else "NA"}</td>
                        <td style="padding: 5px;">{action['date_due'] if action['date_due'] else "NA"}</td>
                    </tr>
                """
                for action in actions
            ]
        )
        res += "</table>"
        return res

    site_info = f"""
        <h3>{context['title']}</h3>

        {format_image(context["image"], "Prevention Initiative Image")}

        <table style='border-collapse: separate;border-spacing: 1em 0.5em;'>
            <tr>
              <td><b>Event Date</b></td>
              <td>{context['event_date']}</td>
            </tr>
            <tr>
              <td><b>Site</b></td>
              <td>{context['site']}</td>
            </tr>
            <tr>
              <td><b>Department</b></td>
              <td>{context['department']}</td>
            </tr>
            <tr>
              <td><b>Functional Location</b></td>
              <td>{context['function_location']}</td>
            </tr>
            <tr>
              <td><b>Equipment</b></td>
              <td>{context['equipment_description']} ({context['object_type']})</td>
            </tr>
            <tr>
              <td><b>Object Part</b></td>
              <td>{context['object_part_description']}</td>
            </tr>
            <tr>
              <td><b>Damage Code</b></td>
              <td>{context['damage_code']}</td>
            </tr>
        </table>
    """

    # setup
    why_summary_text = f"The event occurred due to {context['cause_code']} from a failure in {context['cause_category']}."

    # html output
    html = f"""
        <p>[auto-generated content below]</p>

        {site_info}
        <hr />

        <h4>What happened?</h4>
        <p><b>{why_summary_text}</b></p>
        <p>{context['description']}</p>

        <h4>Why did it happen?</h4>
        <p>{context['reason']}</p>

        <h4>What we learned and want to share</h4>
        <p>{context['shared_learning']}</p>
        """

    html += f"""
        <h4>Actions</h4>
        {format_actions(context['actions'])}

        <p><a href='https://{config.SERVER_NAME}/investigation?id={context['investigation_id']}'>Please open link to review the investigation.</a></p>
    """

    # -----------------------------------------------------

    templateLoader = jinja2.FileSystemLoader(os.path.join("/app/app/email/templates"))
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template("header_description.html")
    html = templ.render(header="", description=html)

    # -----------------------------------------------------

    subject = f"Shared Learnings - {context['title']}"

    # -----------------------------------------------------

    # ? - images embedded in html now, this is no longer required
    # attach image, if any
    # if context["image_path"]:
    #     attachments.append(context["image_path"])
    #     custom_attachment_names.append("Prevention Initiative Image.png")

    # -----------------------------------------------------

    send_email(html, subject, recipients, attachments, custom_attachment_names)

    # ---------------------------------------------------
