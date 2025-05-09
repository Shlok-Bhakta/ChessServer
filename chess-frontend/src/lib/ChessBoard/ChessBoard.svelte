<script lang="ts">
  import { ChessBoardState } from "./ChessBoardState.svelte";
  const CBS = new ChessBoardState();
</script>

<div class="chessboard">
  <div id="board" class="grid grid-cols-8 grid-rows-8 gap-1 w-fit aspect-square">
    {#each CBS.squares as row}
      {#each row as square}
        <div id="square-{square}" class="bg-black aspect-square h-20">{square}</div>
      {/each}
    {/each}
  </div>
</div>
