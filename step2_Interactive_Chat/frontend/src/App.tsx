import React from 'react';
import { Container, CssBaseline, AppBar, Toolbar, Typography, ThemeProvider, createTheme } from '@mui/material';
import Chat from './components/Chat';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">
            Video Highlights Chat
          </Typography>
        </Toolbar>
      </AppBar>
      <Container>
        <Chat />
      </Container>
    </ThemeProvider>
  );
}

export default App;
