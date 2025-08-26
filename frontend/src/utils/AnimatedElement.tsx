// utils/AnimatedElement.tsx
import { useMemo }       from "react";
import type { ReactNode } from "react";
import { motion }        from "framer-motion";

interface AnimatedElementProps {
  children: ReactNode;
}

export default function AnimatedElement({ children }: AnimatedElementProps) {
  const enterX = useMemo(
    () => (Math.random() > 0.5 ? 300 : -300),
    []
  );
  const exitX = useMemo(
    () => (Math.random() > 0.5 ? 300 : -300),
    []
  );

  return (
    <motion.div
      initial={{ x: enterX, opacity: 0 }}
      animate={{ x: 0,      opacity: 1 }}
      exit={{    x: exitX,  opacity: 0 }}
      transition={{ duration: 0.5, ease: "easeInOut" }}
      className="block w-full"
    >
      {children}
    </motion.div>
  );
}
