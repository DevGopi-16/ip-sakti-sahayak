import { useEffect, useState } from 'react';
import { onAuthStateChanged } from 'firebase/auth';

import { auth } from '../firebase';

export default function useAuth() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(
      auth,
      (currentUser) => {
        setUser(currentUser);
        setAuthLoading(false);
        setImgError(false);
      }
    );

    return () => unsubscribe();
  }, []);

  return {
    user,
    setUser,
    authLoading,
    imgError,
    setImgError,
  };
}