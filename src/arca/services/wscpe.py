from __future__ import annotations

import xml.etree.ElementTree as ET

from ..config import ArcaSettings
from ..models.wscpe import WscpeAuth
from ..soap.transport import SoapClient
from ..soap.xml import element_to_data
from ..wsaa.token_provider import WsaaTokenProvider


WSCPE_NS = "https://serviciosjava.afip.gob.ar/wscpe/"

SOAP_ACTIONS = {
    "dummy": "https://serviciosjava.afip.gob.ar/wscpe/dummy",
    "consultarUltNroOrden": "https://serviciosjava.afip.gob.ar/wscpe/consultarUltNroOrden",
    "consultarCPEAutomotor": "https://serviciosjava.afip.gob.ar/wscpe/consultarCPEAutomotor",
    "consultarCPEPorDestino": "https://serviciosjava.afip.gob.ar/wscpe/consultarCPEPorDestino",
}


ET.register_namespace("tns", WSCPE_NS)



def _append_value(parent: ET.Element, value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if item is None:
                continue
            if isinstance(item, list):
                for one in item:
                    child = ET.SubElement(parent, key)
                    _append_value(child, one)
            else:
                child = ET.SubElement(parent, key)
                _append_value(child, item)
        return

    if isinstance(value, bool):
        parent.text = "true" if value else "false"
        return

    parent.text = str(value)



def _build_request_xml(root_name: str, payload: dict[str, object] | None = None) -> str:
    root = ET.Element(f"{{{WSCPE_NS}}}{root_name}")
    if payload:
        _append_value(root, payload)
    return ET.tostring(root, encoding="unicode")


class WSCpeService:
    def __init__(self, settings: ArcaSettings) -> None:
        self.settings = settings
        self.token_provider = WsaaTokenProvider(settings)
        self.soap = SoapClient(
            base_url=settings.wscpe_url,
            timeout_seconds=settings.timeout_seconds,
            verify_tls=settings.verify_tls,
            retries=1,
            retry_backoff_seconds=0.8,
        )

    def _auth(self, *, force_ta: bool = False) -> tuple[WscpeAuth, str, str]:
        ta_result = self.token_provider.get_ta(self.settings.wsid, force_refresh=force_ta)
        auth = WscpeAuth(
            token=ta_result.ticket.token,
            sign=ta_result.ticket.sign,
            cuit_representada=self.settings.cuit_representada,
        )
        return auth, ta_result.source, ta_result.ticket.expiration_time.isoformat()

    def dummy(self) -> dict[str, object]:
        try:
            response = self.soap.call(
                action="dummy",
                body_xml="",
                soap_action=SOAP_ACTIONS["dummy"],
            )
        except Exception:
            response = self.soap.call(
                action="dummy",
                body_xml=_build_request_xml("DummyReq", {}),
                soap_action=SOAP_ACTIONS["dummy"],
            )
        parsed = element_to_data(response)
        return parsed if isinstance(parsed, dict) else {"respuesta": parsed}

    def consultar_ult_nro_orden(
        self,
        *,
        sucursal: int,
        tipo_cpe: int,
        force_ta: bool = False,
    ) -> tuple[dict[str, object], str, str]:
        auth, ta_source, ta_expiration = self._auth(force_ta=force_ta)
        payload = {
            "auth": auth.as_dict(),
            "solicitud": {
                "sucursal": sucursal,
                "tipoCPE": tipo_cpe,
            },
        }

        response = self.soap.call(
            action="consultarUltNroOrden",
            body_xml=_build_request_xml("ConsultarUltNroOrdenReq", payload),
            soap_action=SOAP_ACTIONS["consultarUltNroOrden"],
            namespaces={"tns": WSCPE_NS},
        )
        parsed = element_to_data(response)
        return (parsed if isinstance(parsed, dict) else {"respuesta": parsed}, ta_source, ta_expiration)

    def consultar_cpe_automotor(
        self,
        *,
        cuit_solicitante: int | None = None,
        carta_porte: dict[str, object] | None = None,
        nro_ctg: int | None = None,
        force_ta: bool = False,
    ) -> tuple[dict[str, object], str, str]:
        auth, ta_source, ta_expiration = self._auth(force_ta=force_ta)
        solicitud: dict[str, object] = {}
        if cuit_solicitante is not None:
            solicitud["cuitSolicitante"] = cuit_solicitante
        if carta_porte is not None:
            solicitud["cartaPorte"] = carta_porte
        if nro_ctg is not None:
            solicitud["nroCTG"] = nro_ctg

        payload = {
            "auth": auth.as_dict(),
            "solicitud": solicitud,
        }

        response = self.soap.call(
            action="consultarCPEAutomotor",
            body_xml=_build_request_xml("ConsultarCPEAutomotorReq", payload),
            soap_action=SOAP_ACTIONS["consultarCPEAutomotor"],
            namespaces={"tns": WSCPE_NS},
        )
        parsed = element_to_data(response)
        return (parsed if isinstance(parsed, dict) else {"respuesta": parsed}, ta_source, ta_expiration)

    def consultar_cpe_por_destino(
        self,
        *,
        planta: int,
        fecha_partida_desde: str,
        fecha_partida_hasta: str,
        tipo_carta_porte: int | None = None,
        force_ta: bool = False,
    ) -> tuple[dict[str, object], str, str]:
        auth, ta_source, ta_expiration = self._auth(force_ta=force_ta)
        solicitud: dict[str, object] = {
            "planta": planta,
            "fechaPartidaDesde": fecha_partida_desde,
            "fechaPartidaHasta": fecha_partida_hasta,
        }
        if tipo_carta_porte is not None:
            solicitud["tipoCartaPorte"] = tipo_carta_porte

        payload = {
            "auth": auth.as_dict(),
            "solicitud": solicitud,
        }

        response = self.soap.call(
            action="consultarCPEPorDestino",
            body_xml=_build_request_xml("ConsultarCPEPorDestinoReq", payload),
            soap_action=SOAP_ACTIONS["consultarCPEPorDestino"],
            namespaces={"tns": WSCPE_NS},
        )
        parsed = element_to_data(response)
        return (parsed if isinstance(parsed, dict) else {"respuesta": parsed}, ta_source, ta_expiration)
