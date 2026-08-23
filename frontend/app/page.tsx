"use client";


import { useState } from "react";
import { checkBackend } from "@/lib/api";


export default function Home() {


    const [status, setStatus] = useState("");


    async function handleCheck() {

        try {

            const data = await checkBackend();

            setStatus(
                `Backend Connected 🚀 - ${data.system}`
            );

        } catch (error) {

            setStatus(
                "Backend Not Connected ❌"
            );

        }

    }


    return (

        <main className="
      min-h-screen
      bg-white
      flex
      items-center
      justify-center
    ">


            <section className="text-center">


                <p className="
          text-blue-600
          font-semibold
        ">
                    AI ENGINEER CORE SYSTEM
                </p>


                <h1 className="
          mt-6
          text-5xl
          font-bold
          text-gray-900
        ">
                    Welcome Main Core
                </h1>


                <h2 className="
          mt-4
          text-6xl
          font-bold
          text-blue-600
        ">
                    Budi Cahyono
                </h2>


                <p className="
          mt-6
          text-gray-500
        ">
                    Fullstack AI Engineer Template
                </p>



                <button
                    onClick={handleCheck}
                    className="
          mt-10
          px-6
          py-3
          rounded-xl
          bg-blue-600
          text-white
          hover:bg-blue-700
          "
                >

                    Check Backend Status

                </button>



                {
                    status && (

                        <p className="
              mt-6
              text-blue-600
              font-semibold
            ">

                            {status}

                        </p>

                    )
                }


            </section>


        </main>

    );
}