import React, { useState, useEffect, useRef } from 'react';
import { Box, TextField, IconButton, Paper, Typography, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MessageBubble from './MessageBubble';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState('');
  const [ticketNumber, setTicketNumber] = useState(null);
  const [waitingForConfirmation, setWaitingForConfirmation] = useState(false);
  const messagesEndRef = useRef(null);

  // Gerar ID de usuário único ao carregar o componente
  useEffect(() => {
    const storedUserId = localStorage.getItem('chatUserId');
    if (storedUserId) {
      setUserId(storedUserId);
    } else {
      const newUserId = uuidv4();
      localStorage.setItem('chatUserId', newUserId);
      setUserId(newUserId);
    }
  }, []);

  // Iniciar conversa quando o ID do usuário estiver disponível
  useEffect(() => {
    if (userId && messages.length === 0) {
      // Adicionar mensagem de boas-vindas do sistema
      setMessages([{
        id: uuidv4(),
        content: 'Olá! Sou o assistente de suporte N1. Como posso ajudar você hoje?',
        type: 'bot',
        timestamp: new Date()
      }]);
    }
  }, [userId, messages.length]);

  // Rolar para a mensagem mais recente quando as mensagens mudarem
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    const userMessage = {
      id: uuidv4(),
      content: input,
      type: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Determinar se estamos enviando feedback ou uma nova mensagem
      const endpoint = waitingForConfirmation ? '/feedback' : '/chat';
      
      const response = await axios.post(`http://localhost:8000${endpoint}`, {
        user_id: userId,
        message: input
      });

      // Resetar o estado de espera por confirmação
      if (waitingForConfirmation) {
        setWaitingForConfirmation(false);
      }

      // Verificar se a resposta contém mensagens do bot
      if (response.data && response.data.messages) {
        const incomingBotMessages = response.data.messages
          .filter(msg => msg.type === 'bot') // Filtra apenas mensagens do bot
          .map(msg => ({
            id: msg.id || uuidv4(), // Garante que cada mensagem tenha um ID único
            content: msg.content,
            type: 'bot',
            timestamp: new Date(msg.timestamp) || new Date()
          }));

          if (incomingBotMessages.length > 0) {
            // Use o callback de setMessages para garantir que a atualização seja baseada no estado mais recente
            // Filtra as mensagens recebidas para incluir apenas aquelas cujo ID ainda não existe no estado atual
            setMessages(prevMessages => {
              const existingMessageIds = new Set(prevMessages.map(msg => msg.id));
              const newUniqueBotMessages = incomingBotMessages.filter(msg => !existingMessageIds.has(msg.id));
              return [...prevMessages, ...newUniqueBotMessages];
            });
          }

        // Verificar se a última mensagem do bot está perguntando por confirmação
        const lastIncomingBotMessage = incomingBotMessages[incomingBotMessages.length - 1];
         if (lastIncomingBotMessage && lastIncomingBotMessage.content.includes('Esta solução resolveu o seu problema?')) {
           setWaitingForConfirmation(true);
         }

        // Verificar se há um número de ticket
        if (response.data.ticket_number) {
          setTicketNumber(response.data.ticket_number);
        }
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      
      // Adicionar mensagem de erro
      setMessages(prev => [...prev, {
        id: uuidv4(),
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde.',
        type: 'bot',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        overflow: 'hidden'
      }}
    >
      {ticketNumber && (
        <Box sx={{ p: 1, bgcolor: 'primary.main', color: 'white', textAlign: 'center' }}>
          <Typography variant="body2">
            Ticket #{ticketNumber} aberto para acompanhamento
          </Typography>
        </Box>
      )}
      
      <Box 
        sx={{ 
          flexGrow: 1, 
          p: 2, 
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>
      
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Digite sua mensagem..."
            value={input}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            size="small"
            sx={{ mr: 1 }}
          />
          <IconButton 
            color="primary" 
            onClick={handleSendMessage} 
            disabled={isLoading || input.trim() === ''}
            size="large"
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};

export default ChatInterface;