// Teste "Qual homem da Bíblia você é hoje?" — fonte única do texto (página e PDFs).
// Versículos citados na íntegra: ARA. Os planos citam só a referência.
window.DADOS = {
  perguntas: [
    { q: "Quando um problema grande aparece, sua primeira reação é:", o: [
      ["Resolver do meu jeito, nem que precise dar um jeitinho", ["jaco"]],
      ["Agir na hora e pensar depois", ["pedro"]],
      ["Achar que não dou conta", ["gideao"]],
      ["Manter a calma e fazer o certo, mesmo que demore", ["jose"]] ] },
    { q: "No fim de um dia difícil, você costuma:", o: [
      ["Me isolar e não querer falar com ninguém", ["elias"]],
      ["Ficar no celular até tarde para esquecer", ["davi"]],
      ["Repassar tudo na cabeça e planejar a próxima jogada", ["jaco"]],
      ["Me cobrar por não ter feito mais", ["gideao"]] ] },
    { q: "Sua vida de oração hoje está mais para:", o: [
      ["Oro com força quando aperta, depois esfria", ["pedro"]],
      ["Oro, mas sinto Deus longe", ["elias"]],
      ["Tenho rotina, mas a cabeça vive dispersa", ["davi"]],
      ["Oro pouco, porque prefiro resolver sozinho", ["jaco"]] ] },
    { q: "Quando alguém te ofende ou te trai:", o: [
      ["Respondo no calor do momento", ["pedro"]],
      ["Guardo e espero a hora certa de reagir", ["jaco"]],
      ["Sofro calado e me afasto", ["elias"]],
      ["Escolho perdoar, mesmo doendo", ["jose"]] ] },
    { q: "Sua luta mais escondida é:", o: [
      ["Uma tentação que volta quando estou sozinho ou à toa", ["davi"]],
      ["O medo de não estar à altura", ["gideao"]],
      ["Um cansaço que não passa", ["elias"]],
      ["A vontade de controlar tudo", ["jaco"]] ] },
    { q: "Em casa (ou pensando na família que quer ter), você se vê:", o: [
      ["Presente no corpo, ausente na cabeça", ["davi"]],
      ["Esforçado, mas inseguro para liderar", ["gideao"]],
      ["Firme, mas às vezes duro demais", ["pedro"]],
      ["Constante, mas carregando tudo sozinho", ["jose", "elias"]] ] },
    { q: "Quando Deus parece não responder:", o: [
      ["Insisto e faço acontecer", ["jaco"]],
      ["Desanimo e penso em desistir", ["elias"]],
      ["Peço um sinal antes de dar o próximo passo", ["gideao"]],
      ["Continuo fiel no que tenho para hoje", ["jose"]] ] },
    { q: "Sobre as promessas que você faz:", o: [
      ["Prometo muito no entusiasmo e não cumpro tudo", ["pedro"]],
      ["Evito prometer para não falhar", ["gideao"]],
      ["Cumpro, mesmo quando ninguém vê", ["jose"]],
      ["Cumpro quando me convém", ["jaco"]] ] },
    { q: "Depois de uma grande vitória, você tende a:", o: [
      ["Baixar a guarda", ["davi"]],
      ["Cair num vazio e num desânimo", ["elias"]],
      ["Me empolgar e falar demais", ["pedro"]],
      ["Achar que foi sorte", ["gideao"]] ] },
    { q: "O que mais te faz cair:", o: [
      ["Olhos e mente sem vigilância", ["davi"]],
      ["O orgulho de achar que dou conta sozinho", ["jaco"]],
      ["O impulso", ["pedro"]],
      ["O cansaço e a solidão", ["elias"]] ] },
    { q: "Um amigo descreveria você como:", o: [
      ["Leal e corajoso, mas explosivo", ["pedro"]],
      ["Esforçado, mas sempre se diminuindo", ["gideao"]],
      ["Íntegro e confiável", ["jose"]],
      ["Intenso, de altos e baixos", ["davi"]] ] },
    { q: "O que você mais quer de Deus agora:", o: [
      ["Força para recomeçar", ["elias"]],
      ["Coragem para assumir o meu lugar", ["gideao"]],
      ["Um coração limpo", ["davi"]],
      ["Paz para parar de lutar sozinho", ["jaco"]],
      ["Perseverar no certo sem desanimar", ["jose"]] ] }
  ],

  perfis: {
    jaco: {
      nome: "Jacó", titulo: "O homem que luta sozinho",
      verso: "Já não te chamarás Jacó, e sim Israel, pois como príncipe lutaste com Deus e com os homens e prevaleceste.",
      ref: "Gênesis 32:28",
      retrato: "Você é forte, esperto e não espera ninguém para resolver. O risco é quando essa força vira controle: você luta com todo mundo, até com Deus.",
      forca: "Iniciativa e garra.",
      armadilha: "Resolver no jeitinho e carregar tudo sozinho.",
      cristo: "Jacó só virou Israel quando foi quebrado e se agarrou a Deus. Em Cristo, render-se não é perder: é ser abençoado.",
      plano: [
        ["Gênesis 27:18-24", "Liste onde você tem dado um jeito em vez de ser honesto."],
        ["Gênesis 28:10-22", "Deus encontrou Jacó em fuga. Anote uma promessa de Deus que você esqueceu."],
        ["Gênesis 32:9-12", "Antes de planejar o dia, ore pedindo ajuda. Escreva a oração."],
        ["Gênesis 32:24-30", "Diga a Deus, em voz alta, a área que você não quer soltar."],
        ["Provérbios 3:5-6", "Tome uma decisão da semana pedindo conselho a alguém."],
        ["2 Coríntios 12:9-10", "Conte a um irmão de confiança uma fraqueza real."],
        ["Mateus 11:28-30", "Faça 15 minutos de silêncio sem celular e entregue a Deus a próxima semana."]
      ]
    },
    pedro: {
      nome: "Pedro", titulo: "O homem de coragem sem constância",
      verso: "Eu, porém, roguei por ti, para que a tua fé não desfaleça; tu, pois, quando te converteres, fortalece os teus irmãos.",
      ref: "Lucas 22:32",
      retrato: "Você tem coragem e coração quente. É o primeiro a sair do barco, mas às vezes também o primeiro a afundar.",
      forca: "Lealdade e coragem.",
      armadilha: "O impulso e a falta de constância.",
      cristo: "Jesus orou por Pedro antes da queda e o restaurou depois. Sua fé não depende do seu entusiasmo, mas de quem intercede por você.",
      plano: [
        ["Mateus 14:22-33", "Escreva onde você começou bem e depois afundou."],
        ["Mateus 16:13-23", "Hoje, conte 5 segundos antes de responder a qualquer pessoa."],
        ["Lucas 22:31-34", "Lembre uma promessa que você não cumpriu e cumpra uma parte dela hoje."],
        ["Lucas 22:54-62", "Peça perdão a alguém que você feriu no impulso."],
        ["João 21:15-19", "Responda por escrito: como o meu amor a Cristo aparece na minha agenda?"],
        ["Tiago 1:19-20", "Passe um dia inteiro sem discutir, em casa ou nas redes."],
        ["1 Pedro 5:6-10", "Escolha um hábito pequeno e diário para os próximos 30 dias. Constância vence intensidade."]
      ]
    },
    elias: {
      nome: "Elias", titulo: "O homem cansado depois da batalha",
      verso: "Levanta-te e come, porque o caminho te será sobremodo longo.",
      ref: "1 Reis 19:7",
      retrato: "Você já lutou muito e viu Deus agir. Agora o cansaço pesa e parece que só você ficou de pé.",
      forca: "Zelo por Deus.",
      armadilha: "O isolamento e o esgotamento.",
      cristo: "Deus não deu sermão a Elias: deu pão, sono e uma voz mansa. Cristo chama os cansados para descansar nele (Mateus 11:28).",
      cuidado: "Se o desânimo for profundo ou durar semanas, procure seu pastor e um profissional de saúde. Em crise, ligue 188 (CVV), de graça e a qualquer hora.",
      plano: [
        ["1 Reis 18:36-39", "Escreva 3 vitórias que Deus já te deu."],
        ["1 Reis 19:1-4", "Diga a Deus, com honestidade, como você está."],
        ["1 Reis 19:5-8", "Cuide do corpo hoje: durma 7 horas, coma direito, caminhe 20 minutos."],
        ["1 Reis 19:9-13", "Faça 15 minutos de silêncio sem tela, só ouvindo."],
        ["1 Reis 19:15-18", "Você não está sozinho: ligue para um irmão hoje."],
        ["Salmo 42:5", "Escreva o que te abate e responda com uma verdade da Bíblia."],
        ["Isaías 40:28-31", "Marque um descanso semanal de verdade e proteja esse horário."]
      ]
    },
    davi: {
      nome: "Davi", titulo: "O homem de coração dividido",
      verso: "Cria em mim, ó Deus, um coração puro e renova dentro em mim um espírito inabalável.",
      ref: "Salmo 51:10",
      retrato: "Você é intenso, ama a Deus e tem força para grandes coisas. Mas o ponto fraco aparece nos momentos à toa, quando a guarda baixa.",
      forca: "Paixão e coragem.",
      armadilha: "A tentação no tempo ocioso.",
      cristo: "Davi caiu feio, mas não fugiu de Deus: confessou. Em Cristo há perdão completo e um coração novo.",
      plano: [
        ["2 Samuel 11:1-5", "Identifique o seu terraço: o horário e o lugar em que você costuma cair."],
        ["Mateus 5:27-30", "Corte um acesso: tire o celular do quarto à noite."],
        ["2 Samuel 12:1-13", "Confesse a Deus, sem desculpas, o que precisa ser confessado."],
        ["Salmo 51:1-12", "Ore o Salmo 51 em voz alta."],
        ["Provérbios 4:23-27", "Escreva uma regra para os seus olhos: o que não abre e quando não usa."],
        ["Tiago 5:16", "Escolha um irmão para prestar contas e conte o seu plano a ele."],
        ["Filipenses 4:8", "Troque o tempo à toa por algo que alimenta: leitura, exercício, família."]
      ]
    },
    gideao: {
      nome: "Gideão", titulo: "O homem que se acha pequeno",
      verso: "O SENHOR é contigo, homem valente.",
      ref: "Juízes 6:12",
      retrato: "Você se acha pequeno demais para o que Deus pede. Mas Deus te chama de valente antes de você se sentir valente.",
      forca: "Humildade e sensibilidade.",
      armadilha: "O medo e o hábito de adiar.",
      cristo: "A força não vinha de Gideão, vinha da presença de Deus. Em Cristo, o poder se aperfeiçoa na fraqueza (2 Coríntios 12:9).",
      plano: [
        ["Juízes 6:11-16", "Escreva como você se vê e como Deus te chama."],
        ["Juízes 6:25-27", "Faça hoje uma coisa certa que você vem adiando por medo."],
        ["Juízes 6:36-40", "Deus foi paciente com Gideão. Liste 3 cuidados de Deus com você."],
        ["Juízes 7:2-8", "Ore sobre algo que parece grande demais para você."],
        ["Josué 1:9", "Decore Josué 1:9 e repita ao acordar."],
        ["Efésios 6:10-18", "Conduza uma oração em casa ou com um amigo."],
        ["Filipenses 4:13", "Assuma uma responsabilidade concreta esta semana, em casa, na igreja ou no trabalho."]
      ]
    },
    jose: {
      nome: "José", titulo: "O homem íntegro sob pressão",
      verso: "Vós, na verdade, intentastes o mal contra mim; porém Deus o tornou em bem, para fazer, como vedes agora, que se conserve muita gente em vida.",
      ref: "Gênesis 50:20",
      retrato: "Você tenta fazer o certo mesmo quando ninguém vê e quando o certo custa caro. O desafio é não amargar na espera.",
      forca: "Integridade e constância.",
      armadilha: "Guardar mágoa e cansar de esperar.",
      cristo: "José perdoou quem o traiu e salvou muitos. Cristo fez isso por nós de forma perfeita, e é ele quem sustenta a sua espera.",
      plano: [
        ["Gênesis 37:3-11", "Escreva o que você espera que Deus faça na sua vida."],
        ["Gênesis 39:1-6", "Faça o trabalho de hoje como para o Senhor (Colossenses 3:23)."],
        ["Gênesis 39:7-12", "Decida antes onde você não vai pisar. Diante da tentação, fuja: não negocie."],
        ["Gênesis 40:20-23", "Agradeça a Deus por algo que ainda não mudou."],
        ["Gênesis 45:1-8", "Escreva o seu perdão a alguém (não precisa enviar)."],
        ["Gênesis 50:15-21", "Faça um gesto concreto de bem a quem te feriu."],
        ["Romanos 8:28", "Escreva como Deus usou uma dor sua para o bem e conte a alguém."]
      ]
    }
  },
  ordem: ["jaco", "pedro", "elias", "davi", "gideao", "jose"]
};
