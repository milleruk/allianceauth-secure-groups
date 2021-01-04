from django.db import models
from allianceauth.eveonline.models import (
    EveCorporationInfo,
    EveAllianceInfo,
)
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone

from . import app_settings, filter as smart_filters

if app_settings.discord_bot_active():
    import aadiscordbot

import logging

logger = logging.getLogger(__name__)


class GroupUpdateWebhook(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    webhook = models.TextField()
    extra_message = models.TextField(default="", blank=True)

    def __str__(self):
        return "Group Update Hook for: %s" % self.group.name


class SmartFilter(models.Model):

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, editable=False
    )
    object_id = models.PositiveIntegerField(editable=False)
    filter_object = GenericForeignKey("content_type", "object_id")
    grace_period = models.IntegerField(default=5)

    def __str__(self):
        try:
            return f"{self.filter_object.name}: {self.filter_object.description}"
        except:
            return f"Error: {self.content_type.app_label}:{self.content_type} {self.object_id} Not Found"


class FilterBase(models.Model):

    name = models.CharField(max_length=500)
    description = models.CharField(max_length=500)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name}: {self.description}"

    def process_filter(self, user: User):
        raise NotImplementedError("Please Create a filter!")


class AltCorpFilter(FilterBase):
    alt_corp = models.ForeignKey(EveCorporationInfo, on_delete=models.CASCADE)

    def process_filter(self, user: User):
        return smart_filters.check_alt_corp_on_account(
            user, self.alt_corp.corporation_id
        )


class AltAllianceFilter(FilterBase):
    alt_alli = models.ForeignKey(EveAllianceInfo, on_delete=models.CASCADE)

    def process_filter(self, user: User):
        return smart_filters.check_alt_alli_on_account(user, self.alt_alli.alliance_id)


class SmartGroup(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.CharField(max_length=500, default="", blank=True)
    filters = models.ManyToManyField(SmartFilter)
    last_update = models.DateTimeField(auto_now=True)

    auto_group = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    include_in_updates = models.BooleanField(default=True)

    can_grace = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("access_sec_group", "Can access sec group requests screen."),)

    def __str__(self):
        return "Smart Group :%s" % self.group.name

    def run_checks(self, user: User):
        output = []
        for check in self.filters.all():
            try:
                _filter = check.filter_object
                if _filter is None:
                    logger.warning(f"Failed to run filter for {check}")
                    continue  # Skip as this is broken...
                test_pass = _filter.process_filter(user)
            except:
                test_pass = False
                logger.error("TEST FAILED")  # TODO Make pretty
            _check = {
                "message": check.filter_object.description,
            }
            _check["output"] = test_pass
            _check["filter"] = check
            output.append(_check)
        return output

    def process_checks(self, checks):
        out = True
        for c in checks:
            out = out & c.get("output", False)
        return out

    def check_user(self, user: User):
        checks = self.run_checks(user)
        out = self.process_checks(checks)
        return out


class GracePeriodRecord(models.Model):
    group = models.ForeignKey(SmartGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grace_filter = models.ForeignKey(SmartFilter, on_delete=models.CASCADE)
    expires = models.DateTimeField()

    def __str__(self):
        return "{} - {} - {}".format(self.user, self.group, self.grace_filter)

    def is_expired(self):
        return self.expires < timezone.now()

    def notify_user(self, message):
        # dm user if has discord account and discord bot installed
        if app_settings.discord_bot_active():
            try:
                aadiscordbot.tasks.send_direct_message.delay(
                    self.user.discord.uid, message
                )
            except Exception as e:
                logger.error(e, exc_info=True)
                pass
        else:
            pass