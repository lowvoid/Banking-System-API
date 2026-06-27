from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from django.db import transaction
from .models import BankAccount, Transaction


@receiver(post_save, sender=Transaction)
def update_account_balance(sender, instance, created, **kwargs):
    if not created:
        return

    with transaction.atomic():
        if instance.transaction_type == Transaction.TransactionType.DEPOSIT:
            BankAccount.objects.filter(id=instance.account_id).update(balance=F("balance") + instance.amount)
        elif instance.transaction_type == Transaction.TransactionType.WITHDRAWAL:
            BankAccount.objects.filter(id=instance.account_id).update(balance=F("balance") - instance.amount)
