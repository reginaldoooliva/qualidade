import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { useNavigate } from "react-router-dom"
import { z } from "zod"

import { ShieldCheck } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuth } from "@/features/auth/AuthContext"
import { useLogin } from "@/features/auth/api"
import { getApiError } from "@/lib/api-client"

const schema = z.object({
  login: z.string().min(1, "Informe o login"),
  senha: z.string().min(1, "Informe a senha"),
})

type FormValues = z.infer<typeof schema>

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const loginMutation = useLogin()

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { login: "", senha: "" },
  })

  function onSubmit(values: FormValues) {
    loginMutation.mutate(values, {
      onSuccess: (data) => {
        login(data.access_token, data.usuario)
        navigate("/pecas", { replace: true })
      },
      onError: (error) => {
        form.setError("senha", { message: getApiError(error).detail })
      },
    })
  }

  return (
    <div
      className="flex min-h-svh items-center justify-center bg-background p-4 bg-[length:28px_28px] bg-[image:linear-gradient(color-mix(in_oklab,var(--primary)_7%,transparent)_1px,transparent_1px),linear-gradient(90deg,color-mix(in_oklab,var(--primary)_7%,transparent)_1px,transparent_1px)]"
    >
      <Card className="w-full max-w-sm border-t-4 border-t-primary shadow-lg">
        <CardHeader>
          <div className="mb-1 flex size-11 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-chart-5 text-primary-foreground shadow-sm">
            <ShieldCheck className="size-5" />
          </div>
          <CardTitle className="text-xl">Sistema de Qualidade</CardTitle>
          <CardDescription>Coleta de medidas, Cp/Cpk e Não Conformidade</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="login"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Login</FormLabel>
                    <FormControl>
                      <Input autoFocus autoComplete="username" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="senha"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Senha</FormLabel>
                    <FormControl>
                      <Input type="password" autoComplete="current-password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={loginMutation.isPending}>
                {loginMutation.isPending ? "Entrando..." : "Entrar"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}
