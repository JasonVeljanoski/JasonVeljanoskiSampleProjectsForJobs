import datetime
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename

import jinja2
from app import config, crud, schemas


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
# COMMON HELPERS
# ------------------------------------------------------------------------------------------------------
def action_email_description(db, action_context):
    """ """

    data = {
        "Assigned To": format_user_name(db, action_context.owner_id) or "NA",
        "Members": format_newline_text(format_user_names(db, action_context.member_ids)) or "NA",
        "Supervisor": format_user_name(db, action_context.supervisor_id) or "NA",
        "Privacy": format_privacy(action_context.privacy),
        "Status": format_action_status(action_context.status) or "NA",
        "Priority": format_action_priority(action_context.priority) or "NA",
        "Floc": action_context.functional_location or "NA",
        "Work Center": action_context.work_center or "NA",
        "Start Date": format_date(action_context.start_date) or "NA",
        "Due Date": format_date(action_context.date_due) or "NA",
    }

    description = (
        f"<h3>{format_newline_text(action_context.title)}</h3>" if action_context.title else ""
    )
    description += (
        f"<p>{format_newline_text(action_context.description)}</p>"
        if action_context.description
        else ""
    )
    description += format_kv_table(data)

    description += f"""<p><a href="https://{config.SERVER_NAME}/actions?id={action_context.id}" target="_blank">Please open link to review the ACE action.</a></p>"""

    return description


def group_email_description(db, workgroup_context):
    """ """

    def format_is_active(is_active: bool):
        if not is_active:
            return "Inactive"
        return "Active"

    def format_actions(actions):
        def format_user_name(db, user_id: int):
            user = crud.user.get(db, user_id)
            return user.name if user else None

        if not actions:
            return "No Actions."

        res = """<table border="2" style="border-collapse:collapse; border-spacing: 0 10px;">
                        <tr>
                            <th style="text-align: left; padding: 5px;">Title</th>
                            <th style="text-align: left; padding: 5px;">Source</th>
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
                            <td style="padding: 5px;"><a href='{action.link}' target="_blank">{action.title}</a></td>
                            <td style="padding: 5px;">{action.type.replace("_", " ")}</td>
                            <td style="padding: 5px;">{format_user_name(db, action.owner_id) if action.owner_id else "NA"}</td>
                            <td style="padding: 5px;">{format_action_priority(action.priority) if action.priority else "NA"}</td>
                            <td style="padding: 5px;">{format_action_status(action.status) if action.status else "NA"}</td>
                            <td style="padding: 5px;">{format_date(action.date_due) if action.date_due else "NA"}</td>
                        </tr>
                    """
                for action in actions
            ]
        )
        res += "</table>"
        return res

    data = {
        "Assigned To": format_user_name(db, workgroup_context.owner_id) or "NA",
        "Members": format_newline_text(format_user_names(db, workgroup_context.member_ids)) or "NA",
        "Admins": format_newline_text(format_user_names(db, workgroup_context.admin_ids)) or "NA",
        "Privacy": format_privacy(workgroup_context.privacy) or "NA",
        "Floc": workgroup_context.functional_location or "NA",
        "Is Active": format_is_active(workgroup_context.is_active) or "NA",
    }

    description = (
        f"<h3>{format_newline_text(workgroup_context.title)}</h3>"
        if workgroup_context.title
        else ""
    )
    description += (
        f"<p>{format_newline_text(workgroup_context.description)}</p>"
        if workgroup_context.description
        else ""
    )
    description += format_kv_table(data)

    description += f"<h4>Actions</h4>"
    description += format_actions(workgroup_context.actions)

    description += f"""<p><a href="https://{config.SERVER_NAME}/groups?id={workgroup_context.id}" target="_blank">Please open link to review the ACE group.</a></p>"""

    return description


# ------------------------------------------------------------------------------------------------------


def send_email(html, subject, recipeints, attachments=[]):
    from app.utils import settings

    def turn_off_emails(recipeints):
        print(f"\n\n\nEmail would sent to {recipeints}\n\n\n")
        # export email to html file instead
        with open("test.html", "w") as f:
            f.write(html)
        return False

    SMTP_HOST = "localrelay.fmg.local"
    SMTP_PORT = 25
    SMTP_USER = "noreply.ace@fmgl.com.au"

    # handle single recipient
    if type(recipeints) != list:
        recipeints = [recipeints]

    if not config.PROD_MODE:
        subject = f"({config.ENV}) - {subject}"

        email_whitelist = settings.get_backend_settings().uat_email_whitelist
        if email_whitelist:
            recipeints = [r for r in recipeints if r in email_whitelist]

    if config.DEV_MODE:
        turn_off_emails(recipeints)

    if config.ENV == "uat":
        pass

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(recipeints)
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html"))

        # -----------------------------

        for f in attachments:
            with open(f, "rb") as fp:
                part = MIMEApplication(fp.read(), Name=basename(f))

            # After the file is closed
            part["Content-Disposition"] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)

        # -----------------------------

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            print(f"\n\n\nSuccessfully sent to {recipeints}\n\n\n")
            server.sendmail(SMTP_USER, recipeints, msg.as_string())
    except:
        pass


# ------------------------------------------------------------------------------------------------------


def feedback_email(db, recipients, subject, header, feedback_context):
    def construct_email_description(db, feedback_context):
        """ """

        def format_reason(reason: int):
            if reason == schemas.enums.FeedbackReason.BUG:
                return "Bug"
            elif reason == schemas.enums.FeedbackReason.GENERAL_FEEDBACK:
                return "General Feedback"
            return None

        def format_status(status: int):
            if status == schemas.enums.FeedbackStatusEnum.OPEN:
                return "Open"
            elif status == schemas.enums.FeedbackStatusEnum.ON_HOLD:
                return "On Hold"
            elif status == schemas.enums.FeedbackStatusEnum.CLOSED_COMPLETE:
                return "Closed (Complete)"
            elif status == schemas.enums.FeedbackStatusEnum.CLOSED_DUPLICATE:
                return "Closed (Duplicate)"
            elif status == schemas.enums.FeedbackStatusEnum.CLOSED_FEEDBACK_ONLY:
                return "Closed (Feedback Only)"
            return None

        # -----------------------------------------------------

        # Setup
        _owner = crud.user.get(db, feedback_context.created_by_id)
        data = {
            "Feedback Type": format_reason(feedback_context.reason),
            "Created By": f"{_owner.name} ({_owner.email})",
            "Status": format_status(feedback_context.status),
        }

        description = f"<h3>{format_newline_text(feedback_context.title)}</h3>"
        description += "<br/>"
        description += format_kv_table(data)
        description += f"<h4>Page Description</h4>{format_newline_text(feedback_context.page)}"
        description += f"<h4>Summary</h4>{format_newline_text(feedback_context.summary)}"
        description += f"<h4>How to Replicate</h4>{format_newline_text(feedback_context.replicate)}"
        description += "<br/><br/>"
        description += f"""<p><a href="https://{config.SERVER_NAME}/feedback?id={feedback_context.id}" target="_blank">Please open link to review the feedback item.</a></p>"""

        return description

    # -----------------------------------------------------

    templateLoader = jinja2.FileSystemLoader(os.path.join("/app/app/email/templates"))
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template("header_description.html")
    html = templ.render(
        header=header, description=construct_email_description(db, feedback_context)
    )

    send_email(html, subject, recipients)


# ------------------------------------------------------------------------------------------------------


def action_email(db, recipients, subject, header, action_context):
    templateLoader = jinja2.FileSystemLoader(os.path.join("/app/app/email/templates"))
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template("header_description.html")
    html = templ.render(header=header, description=action_email_description(db, action_context))

    send_email(html, subject, recipients)


# ------------------------------------------------------------------------------------------------------


def workgroup_email(db, recipients, subject, header, workgroup_context):
    templateLoader = jinja2.FileSystemLoader(os.path.join("/app/app/email/templates"))
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template("header_description.html")
    html = templ.render(header=header, description=group_email_description(db, workgroup_context))

    send_email(html, subject, recipients)


# ------------------------------------------------------------------------------------------------------


def action_comment_email(db, subject, header, comment_context):
    def construct_email_description(db, comment_context):
        """ """
        description = (
            f"<h3>You have been mentioned in a comment by {comment_context['created_by']}.</h3>"
        )

        description += (
            f"<p>{format_newline_text(comment_context['comment'])}</p>"
            if comment_context["comment"]
            else ""
        )

        description += f"""<p style="font-family: sans-serif; font-size: 18px; font-weight: bold; margin-top: 0px; color: #355bb7">Action Details</p>"""
        description += action_email_description(db, comment_context["action"])

        return description

    # -----------------------------------------------------

    templateLoader = jinja2.FileSystemLoader(os.path.join("/app/app/email/templates"))
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template("header_description.html")
    html = templ.render(header=header, description=construct_email_description(db, comment_context))

    recipients = get_recipients_from_comment(comment_context["comment"])
    send_email(html, subject, recipients)


# ------------------------------------------------------------------------------------------------------


def group_comment_email(db, subject, header, comment_context):
    def construct_email_description(db, comment_context):
        """ """
        description = (
            f"<h3>You have been mentioned in a comment by {comment_context['created_by']}.</h3>"
        )

        description += (
            f"<p>{format_newline_text(comment_context['comment'])}</p>"
            if comment_context["comment"]
            else ""
        )

        description += f"""<p style="font-family: sans-serif; font-size: 18px; font-weight: bold; margin-top: 0px; color: #355bb7">Group Details</p>"""
        description += group_email_description(db, comment_context["group"])

        return description

    # -----------------------------------------------------

    templateLoader = jinja2.FileSystemLoader(os.path.join("/app/app/email/templates"))
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template("header_description.html")
    html = templ.render(header=header, description=construct_email_description(db, comment_context))

    recipients = get_recipients_from_comment(comment_context["comment"])
    send_email(html, subject, recipients)
