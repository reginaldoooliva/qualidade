import { createBrowserRouter, Navigate } from "react-router-dom"

import { AppShell } from "@/components/layout/AppShell"
import { LoginPage } from "@/features/auth/LoginPage"
import { RequireAuth } from "@/features/auth/RequireAuth"
import { AnalisePage } from "@/features/analise/AnalisePage"
import { ColetaDetailPage } from "@/features/coleta/ColetaDetailPage"
import { NovaColetaPage } from "@/features/coleta/NovaColetaPage"
import { EtapaDetailPage } from "@/features/etapas/EtapaDetailPage"
import { AbrirNCPage } from "@/features/nao_conformidade/AbrirNCPage"
import { NaoConformidadeDetailPage } from "@/features/nao_conformidade/NaoConformidadeDetailPage"
import { NaoConformidadesListPage } from "@/features/nao_conformidade/NaoConformidadesListPage"
import { PecaDetailPage } from "@/features/pecas/PecaDetailPage"
import { PecasListPage } from "@/features/pecas/PecasListPage"
import { PlanoAcaoDetailPage } from "@/features/plano_acao/PlanoAcaoDetailPage"
import { PlanosAcaoListPage } from "@/features/plano_acao/PlanosAcaoListPage"
import { RelatoriosPage } from "@/features/relatorios/RelatoriosPage"
import { UsuariosPlaceholderPage } from "@/features/usuarios/UsuariosPlaceholderPage"

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppShell />,
        children: [
          { path: "/", element: <Navigate to="/pecas" replace /> },
          { path: "/coleta/nova", element: <NovaColetaPage /> },
          { path: "/coleta/:rodadaId", element: <ColetaDetailPage /> },
          { path: "/analise", element: <AnalisePage /> },
          { path: "/nao-conformidades", element: <NaoConformidadesListPage /> },
          { path: "/nao-conformidades/nova", element: <AbrirNCPage /> },
          { path: "/nao-conformidades/:ncId", element: <NaoConformidadeDetailPage /> },
          { path: "/planos-acao", element: <PlanosAcaoListPage /> },
          { path: "/planos-acao/:planoId", element: <PlanoAcaoDetailPage /> },
          { path: "/pecas", element: <PecasListPage /> },
          { path: "/pecas/:pecaId", element: <PecaDetailPage /> },
          { path: "/pecas/:pecaId/etapas/:etapaId", element: <EtapaDetailPage /> },
          {
            element: <RequireAuth perfis={["analista_qualidade", "gestor_qualidade"]} />,
            children: [{ path: "/relatorios", element: <RelatoriosPage /> }],
          },
          {
            element: <RequireAuth perfis={["gestor_qualidade"]} />,
            children: [{ path: "/usuarios", element: <UsuariosPlaceholderPage /> }],
          },
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/" replace /> },
])
