import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import ReactMarkdown from 'react-markdown';

const MessageBubble = ({ message }) => {
  const { content, type, timestamp } = message;
  
  // Formatar timestamp
  const formattedTime = new Date(timestamp).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  });
  
  // Definir estilos com base no tipo de mensagem
  const getBubbleStyles = () => {
    const baseStyles = {
      maxWidth: '80%',
      p: 1.5,
      mb: 1,
      borderRadius: 2,
    };
    
    switch (type) {
      case 'user':
        return {
          ...baseStyles,
          bgcolor: 'primary.main',
          color: 'white',
          alignSelf: 'flex-end',
          borderBottomRightRadius: 0,
        };
      case 'bot':
        return {
          ...baseStyles,
          bgcolor: 'grey.100',
          color: 'text.primary',
          alignSelf: 'flex-start',
          borderBottomLeftRadius: 0,
        };
      case 'system':
        return {
          ...baseStyles,
          bgcolor: 'grey.200',
          color: 'text.secondary',
          alignSelf: 'center',
          fontStyle: 'italic',
        };
      default:
        return baseStyles;
    }
  };
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', ...getBubbleStyles() }}>
      <ReactMarkdown>{content}</ReactMarkdown>
      <Typography variant="caption" sx={{ alignSelf: type === 'user' ? 'flex-start' : 'flex-end', opacity: 0.7 }}>
        {formattedTime}
      </Typography>
    </Box>
  );
};

export default MessageBubble;