from django.db import models


class TransactionEntryType:
    IN = 'IN'
    OUT = 'OUT'
    CHOICES = (
        (IN, 'Зачисление'),
        (OUT, 'Отчисление')
    )


class TransactionEntry(models.Model):
    # TODO писать при переводе через админку
    date = models.DateField(auto_now_add=True)
    entry_type = models.CharField(
        max_length=3,
        choices=TransactionEntryType.CHOICES,
        default=TransactionEntryType.IN,
    )
    # TODO what does DO_NOTHING do?
    master = models.ForeignKey('masters.Master', on_delete=models.DO_NOTHING,
                               related_name='+')
    value = models.PositiveIntegerField()
    order = models.ForeignKey('orders.Order', on_delete=models.DO_NOTHING,
                              related_name='+')
