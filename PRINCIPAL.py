import requests
import pandas as pd
import xlsxwriter

consolidado_acoes=pd.DataFrame()

lista_de_acoes_do_ibov = pd.read_excel("IBOV.xlsx")
total=len(lista_de_acoes_do_ibov)

contador=1
for codigo_acao in lista_de_acoes_do_ibov["Código"]: 

  url = "https://www.fundamentus.com.br/detalhes.php?papel="+(codigo_acao)


  header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
  }

  r = requests.get(url, headers=header)

  dados_do_site_fundamentus = pd.read_html(r.text,decimal=",",thousands=".") #passo mais argumentos para que a função já identifica e determina qual caractere deve marcar os decimais e milhares
  #print(dados_do_site_fundamentus) #indice da tebela que está sendo acessada

  # print(dados_do_site_fundamentus)
  dados_do_site_fundamentus[0]=dados_do_site_fundamentus[0].transpose()
  dados_do_site_fundamentus[1]=dados_do_site_fundamentus[1].transpose()

  informacoes_1=dados_do_site_fundamentus[0].iloc[:2,:] #funcao iloc puxa a matriz que será selecionada
  informacoes_2=dados_do_site_fundamentus[0].iloc[2:,:] #essas novas tabelas herdam os index anteriores

  informacoes_3=dados_do_site_fundamentus[1].iloc[:2,:] #essas novas tabelas herdam os index anteriores
  informacoes_4=dados_do_site_fundamentus[1].iloc[2:,:] #essas novas tabelas herdam os index anteriores

  #agora temos que resetar os index das tabelas novas
  informacoes_2=informacoes_2.reset_index(drop=True) #nova tabela com index zerados
  informacoes_4=informacoes_4.reset_index(drop=True)

  dados_do_site_fundamentus[2] = dados_do_site_fundamentus[2].transpose()
  InformacaoIndicadores1 = dados_do_site_fundamentus[2].iloc[2:4, 1:12]
  InformacaoIndicadores2 = dados_do_site_fundamentus[2].iloc[4:6, 1:12]

  InformacaoIndicadores2 = InformacaoIndicadores2.reset_index(drop=True)  # nova tabela com index zerados
  InformacaoIndicadores1 = InformacaoIndicadores1.reset_index(drop=True)

  acao=pd.concat([informacoes_1,informacoes_2,informacoes_3,informacoes_4,InformacaoIndicadores1,InformacaoIndicadores2],axis=1,join="inner")
  #concatenar na horizontal usando o axis=1

  acao.columns=acao.iloc[0] #corrigindo o cabeçalho-função .columns chama o cabeçalho
  #função iloc é boa p criar um objeto composto por linhas ou fatias de uma lista

  acao=acao.drop(0)
  print("O papel {} foi adicionado a planilha - contador {}/{}".format(codigo_acao,contador,total))
  consolidado_acoes=consolidado_acoes.append(acao,sort=False)
  #adiciona o dado consultatdo a planilha excel criada no inicio

  contador+=1

consolidado_acoes.columns=[coluna.replace("?","") for coluna in consolidado_acoes.columns]
#replace: substitui algo por alguma coisa-->built in python
consolidado_acoes=consolidado_acoes.reset_index(drop=True) #ao colocar true eu digo que não quero que o index anterior seja armazenado

#correção de datas
consolidado_acoes["Data últ cot"]=pd.to_datetime(consolidado_acoes["Data últ cot"],errors="ignore",format="%d/%m/%y")
consolidado_acoes["Últ balanço processado"]=pd.to_datetime(consolidado_acoes["Últ balanço processado"],errors="ignore",format="%d/%m/%y")

#correção de numeros
consolidado_acoes["Vol $ méd (2m)"]=pd.to_numeric(consolidado_acoes["Vol $ méd (2m)"],errors="coerce")
consolidado_acoes["Valor de mercado"]=pd.to_numeric(consolidado_acoes["Valor de mercado"],errors="coerce")
consolidado_acoes["Nro. Ações"]=pd.to_numeric(consolidado_acoes["Nro. Ações"],errors="coerce")

consolidado_acoes=pd.DataFrame(consolidado_acoes)

maior_valor_de_mercado=consolidado_acoes.loc[consolidado_acoes["Valor de mercado"].idxmax()]
#função loc responde com os dados da linha chamada com seus respectivos títulos

acoes_por_setor=consolidado_acoes.groupby(["Setor"]).count()["Papel"]
#agrupa pelo argumento passado em groupy e realiza a operação do método count ou qualquer ouutro método passado

# acoes_por_setor=consolidado_acoes.groupby(["Setor"]).sum()["Valor de mercad"]
#no exemplo acima, agrupou por setor o total de valor de mercado

consolidado_acoes=consolidado_acoes.replace("-","")


consolidado_acoes.to_excel("consolidado ações.xlsx",index=False,engine='xlsxwriter')