import { logException } from '../sentry.config';

const Home = () => {
  const handleError = () => {
    try {
      // Some code that may throw an error
      throw new Error("Test error");
    } catch (error) {
      logException(error as Error);
    }
  };

  return (
    <div>
      <h1>Hello!</h1>
      <button onClick={handleError}>Trigger Error</button>
    </div>
  );
};

export default Home;
