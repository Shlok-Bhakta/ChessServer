<script lang="ts">
  import { ChessBoardState } from "./ChessBoardState.svelte";
  const CBS = new ChessBoardState();
</script>

<div class="chessboard">
  <div id="board" class="grid grid-cols-10 grid-rows-10 w-fit aspect-square">
    {#each [" ", "a", "b", "c", "d", "e", "f", "g", "h", " "] as col}
      <div class="flex justify-center items-center col-header text-center text-text">{col}</div>
    {/each}
    {#each CBS.board as row}
      <div class="flex justify-center items-center col-header text-center text-text">{row[0].row}</div>
      {#each row as square}
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div id="{square.row}{square.col}" class="
        {square.color == "white" ? "bg-[#D1E1E0]" : "bg-[#659998]"}
        aspect-square h-20
        {square.color == "white" ? "text-black" : "text-white"}"
        >
          {#if square.piece.type != "empty"}
            <img src={CBS.getImageFromPiece(square.piece)} alt="piece" class="w-full h-full" />
          {/if}
          {#if square.piece.type == "empty"}
            <div class="w-full h-full"></div>
          {/if}
        </div>
      {/each}
      <div class="flex justify-center items-center col-header text-center text-text">{row[0].row}</div>
    {/each}
    {#each [" ", "a", "b", "c", "d", "e", "f", "g", "h", " "] as col}
      <div class="flex justify-center items-center col-header text-center text-text">{col}</div>
    {/each}
  </div>
</div>
