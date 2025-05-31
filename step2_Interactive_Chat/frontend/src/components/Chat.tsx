import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';

interface Highlight {
  id: string;
  description: string;
  timestamp: number;
  similarity_score: number;
  video_name: string;
}

const Chat: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const formatVideoTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)} seconds`;
    }
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toFixed(1).padStart(4, '0')} minutes`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/chat/question', { text: question });
      setHighlights(response.data);
    } catch (err) {
      setError('Failed to get highlights. Please try again.');
      console.error('Error fetching highlights:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Ask a question about the video"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            variant="outlined"
            margin="normal"
            disabled={loading}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading || !question.trim()}
            sx={{ mt: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Ask'}
          </Button>
        </form>
      </Paper>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Relevant Highlights
        </Typography>
        <List>
          {highlights.map((highlight) => (
            <ListItem key={highlight.id} divider>
              <ListItemText
                primary={highlight.description}
                secondary={`${highlight.video_name} • At ${formatVideoTime(highlight.timestamp)} • ${(highlight.similarity_score * 100).toFixed(1)}% relevant`}
              />
            </ListItem>
          ))}
          {highlights.length === 0 && !loading && (
            <ListItem>
              <ListItemText
                primary="No highlights found. Try asking a question!"
                sx={{ textAlign: 'center', color: 'text.secondary' }}
              />
            </ListItem>
          )}
        </List>
      </Paper>
    </Box>
  );
};

export default Chat; 