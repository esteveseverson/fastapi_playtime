from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fastapi_playtime.database import get_session
from fastapi_playtime.models.agendamento import Agendamento
from fastapi_playtime.models.quadra import Quadra
from fastapi_playtime.models.user import User
from fastapi_playtime.schemas.agendamento import (
    AgendamentoBase,
    AgendamentoOut,
)
from fastapi_playtime.security import get_current_user
from fastapi_playtime.utils.datetime_format import (
    format_data,
    gmt_to_utc,
    utc_to_gmt,
)

router = APIRouter(prefix='/agendamento', tags=['Agendamento'])

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/', response_model=AgendamentoOut, status_code=HTTPStatus.CREATED
)
def create_agendamento(
    agendamento: AgendamentoBase,
    session: T_Session,
    current_user: T_CurrentUser,
):
    quadra = (
        session.query(Quadra)
        .filter(Quadra.id == agendamento.id_quadra)
        .first()
    )
    if not quadra:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Quadra não encontrada'
        )

    if not quadra.disponivel:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Quadra não está disponível para agendamento',
        )
    
    hora_local = datetime.now()

    if hora_local.date() > agendamento.data:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='A data do agendamento já passou.',
        )

    if hora_local.date() == agendamento.data:
        if hora_local.time() > agendamento.inicio:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='A hora do agendamento já passou.',
            )

    data = agendamento.data

    data_utc, inicio_utc, fim_utc = gmt_to_utc(
        agendamento.data, agendamento.inicio, agendamento.fim
    )

    conflito = (
        session.query(Agendamento)
        .filter(
            Agendamento.id_quadra == agendamento.id_quadra,
            Agendamento.data == data,
            Agendamento.inicio < fim_utc,
            Agendamento.fim > inicio_utc,
        )
        .first()
    )
    if conflito:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Conflito de horário para esta quadra',
        )

    novo_agendamento = Agendamento(
        id_quadra=agendamento.id_quadra,
        id_usuario=current_user.id,
        data=data_utc,
        inicio=inicio_utc,
        fim=fim_utc,
    )

    session.add(novo_agendamento)
    session.commit()
    session.refresh(novo_agendamento)

    # buildando o retorno diferente do que é armazenado no banco:
    return_novo_agendamento = {
        'id': novo_agendamento.id,
        'id_quadra': agendamento.id_quadra,
        'id_usuario': current_user.id,
        'data': agendamento.data,
        'inicio': agendamento.inicio,
        'fim': agendamento.fim,
    }

    return return_novo_agendamento


@router.get('/', response_model=list[list[AgendamentoOut]])
def list_agendamentos(session: T_Session, current_user: T_CurrentUser):
    if current_user.perfil != 'admin':
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED,
            detail='Somente administradores podem ver todos agendamentos',
        )

    agendamentos = session.query(Agendamento).order_by(
        Agendamento.data, Agendamento.inicio
    )

    return_agendamentos = []
    agendamentos_futuros = []
    agendamentos_passados = []
    for agendamento in agendamentos:
        inicio_local, fim_local = utc_to_gmt(
            agendamento.data, agendamento.inicio, agendamento.fim
        )

        data, inicio, fim = format_data(
            agendamento.data, inicio_local, fim_local
        )

        if agendamento.data > (datetime.now()).date():
            agendamentos_futuros.append({
                'id': agendamento.id,
                'id_quadra': agendamento.id_quadra,
                'id_usuario': agendamento.id_usuario,
                'data': data,
                'inicio': inicio,
                'fim': fim,
            })
        else:
            agendamentos_passados.append({
                'id': agendamento.id,
                'id_quadra': agendamento.id_quadra,
                'id_usuario': agendamento.id_usuario,
                'data': data,
                'inicio': inicio,
                'fim': fim,
            })

    return_agendamentos.append(agendamentos_passados)
    return_agendamentos.append(agendamentos_futuros)
    return return_agendamentos


@router.get('/{agendamento_id}', response_model=AgendamentoOut)
def get_agendamento(agendamento_id: int, session: T_Session):
    agendamento = (
        session.query(Agendamento)
        .filter(Agendamento.id == agendamento_id)
        .first()
    )
    if not agendamento:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Agendamento não encontrado',
        )

    inicio_local, fim_local = utc_to_gmt(agendamento.inicio, agendamento.fim)

    data, inicio, fim = format_data(agendamento.data, inicio_local, fim_local)

    return_agendamento = {
        'id': agendamento.id,
        'id_quadra': agendamento.id_quadra,
        'id_usuario': agendamento.id_usuario,
        'data': data,
        'inicio': inicio,
        'fim': fim,
    }

    return return_agendamento


@router.delete('/{agendamento_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_agendamento(
    agendamento_id: int, session: T_Session, current_user: T_CurrentUser
):
    agendamento = (
        session.query(Agendamento)
        .filter(Agendamento.id == agendamento_id)
        .first()
    )
    if not agendamento:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Agendamento não encontrado',
        )

    if (agendamento.id_usuario != current_user.id) and (
        current_user.perfil != 'admin'
    ):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Apenas administradores ou donos do horario podem excluir',
        )

    session.delete(agendamento)
    session.commit()

    return {'message': 'Agendamento cancelado.'}
