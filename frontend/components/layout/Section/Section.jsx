import styles from "./Section.module.css";

/**
 * Global section primitive.
 * Provides: width:100%; position:relative; + configurable padding-block.
 *
 * Props:
 *   py  — padding-top AND bottom (default "80px")
 *   pt  — override padding-top only
 *   pb  — override padding-bottom only
 *   id  — optional anchor id
 *   className — optional extra CSS class
 */
export default function Section({
  children,
  className = "",
  id,
  py = "80px",
  pt,
  pb,
}) {
  return (
    <section
      id={id}
      className={`${styles.section} ${className}`.trim()}
      style={{
        paddingTop:    pt ?? py,
        paddingBottom: pb ?? py,
      }}
    >
      {children}
    </section>
  );
}
