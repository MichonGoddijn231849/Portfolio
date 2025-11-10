from airflow.sensors.base import BaseSensorOperator
from airflow.hooks.base import BaseHook
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient


class SPBlobSensor(BaseSensorOperator):
    """
    Poll the container until at least one *.csv appears.
    Reads tenant_id, client_id, client_secret, account_name from a
    Generic connection (e.g. azure_sp_blob).
    """

    template_fields = ("container_name", "file_suffix")

    def __init__(self, conn_id, container_name, file_suffix=".csv", **kwargs):
        super().__init__(**kwargs)
        self.conn_id = conn_id
        self.container_name = container_name
        self.file_suffix = file_suffix

    def _container_client(self):
        x = BaseHook.get_connection(self.conn_id).extra_dejson
        cred = ClientSecretCredential(
            tenant_id=x["tenant_id"],
            client_id=x["client_id"],
            client_secret=x["client_secret"],
        )
        svc = BlobServiceClient(
            f"https://{x['account_name']}.blob.core.windows.net",
            credential=cred,
        )
        return svc.get_container_client(self.container_name)

    def poke(self, context):
        cont = self._container_client()
        blobs = [b.name for b in cont.list_blobs() if b.name.endswith(self.file_suffix)]
        self.log.info("Found %d *.csv blobs", len(blobs))
        return bool(blobs)
